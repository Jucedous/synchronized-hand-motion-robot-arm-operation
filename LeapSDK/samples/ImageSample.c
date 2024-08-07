/* Copyright (C) 2012-2017 Ultraleap Limited. All rights reserved.
 *
 * Use of this code is subject to the terms of the Ultraleap SDK agreement
 * available at https://central.leapmotion.com/agreements/SdkAgreement unless
 * Ultraleap has signed a separate license agreement with you or your
 * organisation.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include "LeapC.h"
#include "ExampleConnection.h"

time_t last_fist_time = 0;
int fist_detected = 0;
const int WAIT_SECONDS = 1;

/** Callback for when the connection opens. */
static void OnConnect(void){
  printf("Connected.\n");
}

/** Callback for when a device is found. */
static void OnDevice(const LEAP_DEVICE_INFO *props){
  printf("Found device %s.\n", props->serial);
}


typedef struct {
    float newX;
    float newY;
    float newZ;
    float newYaw;
    float newIndexThumbDistance;
} Hand_Status;

#define FILTER_SIZE 10

typedef struct {
    float bufferX[FILTER_SIZE];
    float bufferY[FILTER_SIZE];
    float bufferZ[FILTER_SIZE];
    float bufferYaw[FILTER_SIZE];
    float bufferIndexThumbDistance[FILTER_SIZE];
    int index;
    int count;
    float previousX;
    float previousY;
    float previousZ;
    float originX;
    float originY;
    float originZ;
    float previousYaw;
    float previousThumbIndexDistance;
} MovingAverageFilter;


Hand_Status applyMovingAverageFilter(MovingAverageFilter* state, float newX, float newY, float newZ, float newYaw, float newIndexThumbDistance) {
    Hand_Status this_hand = {0, 0, 0, 0, 0};
    if (!state) return this_hand;

    state->bufferX[state->index] = newX;
    state->bufferY[state->index] = newY;
    state->bufferZ[state->index] = newZ;
    state->bufferYaw[state->index] = newYaw;
    state->bufferIndexThumbDistance[state->index] = newIndexThumbDistance;

    state->index = (state->index + 1) % FILTER_SIZE;
    if (state->count < FILTER_SIZE) state->count++;

    float sumX = 0, sumY = 0, sumZ = 0, sumYaw = 0, sumIndexThumbDistance = 0;
    for (int i = 0; i < state->count; i++) {
        sumX += state->bufferX[i];
        sumY += state->bufferY[i];
        sumZ += state->bufferZ[i];
        sumYaw += state->bufferYaw[i];
        sumIndexThumbDistance += state->bufferIndexThumbDistance[i];
    }
    this_hand.newX = sumX / state->count;
    this_hand.newY = sumY / state->count;
    this_hand.newZ = sumZ / state->count;
    this_hand.newYaw = sumYaw / state->count;
    this_hand.newIndexThumbDistance = sumIndexThumbDistance / state->count;

    return this_hand;
}

void resetMovingAverageFilter(MovingAverageFilter* filter) {
    for(int i = 0; i < FILTER_SIZE; i++) {
        filter->bufferX[i] = 0.0f;
        filter->bufferY[i] = 0.0f;
        filter->bufferZ[i] = 0.0f;
        filter->bufferYaw[i] = 0.0f;
        filter->bufferIndexThumbDistance[i] = 0.0f;
    }

    filter->index = 0;
    filter->count = 0;

    filter->previousX = 0.0f;
    filter->previousY = 0.0f;
    filter->previousZ = 0.0f;
    filter->previousYaw = 0.0f;
    filter->previousThumbIndexDistance = 0.0f;
}

float position_change_threshold = 2.0;
float yaw_change_threshold = 1.0;
float thumb_index_change_threshold = 5.0; 
int no_hand_message_printed = 0;
MovingAverageFilter leftHandFilter = {0};
MovingAverageFilter rightHandFilter = {0}; 

static void OnFrame(const LEAP_TRACKING_EVENT *frame){
  Hand_Status leftHandStatus, rightHandStatus;
  double printX, printY, printZ, printYaw, printIndexThumbDistance;
  bool hasLeftHand = false, hasRightHand = false;
if (frame->nHands > 0) {
  no_hand_message_printed = 0;
  for(uint32_t h = 0; h < frame->nHands; h++){
    LEAP_HAND* hand = &frame->pHands[h];
    float palm_x = hand->palm.position.x;
    float palm_y = hand->palm.position.y;
    float palm_z = hand->palm.position.z;

    float thumb_tip_x = hand->digits[0].distal.next_joint.x;
    float thumb_tip_y = hand->digits[0].distal.next_joint.y;
    float thumb_tip_z = hand->digits[0].distal.next_joint.z;
    float index_tip_x = hand->digits[1].distal.next_joint.x;
    float index_tip_y = hand->digits[1].distal.next_joint.y;
    float index_tip_z = hand->digits[1].distal.next_joint.z;

    float thumb_to_palm_distance = sqrt(pow(thumb_tip_x - palm_x, 2) + pow(thumb_tip_y - palm_y, 2) + pow(thumb_tip_z - palm_z, 2));
    float index_to_palm_distance = sqrt(pow(index_tip_x - palm_x, 2) + pow(index_tip_y - palm_y, 2) + pow(index_tip_z - palm_z, 2));
    // float distance_threshold = 70; 
    // int fingertips_extended = (thumb_to_palm_distance < distance_threshold) && (index_to_palm_distance < distance_threshold);

    float thumb_index_distance = sqrt(pow(thumb_tip_x - index_tip_x, 2) + pow(thumb_tip_y - index_tip_y, 2) + pow(thumb_tip_z - index_tip_z, 2)) - 75;
    // int fingers_touching = (thumb_index_distance < 30) && fingertips_extended;

    LEAP_QUATERNION rotation = hand->palm.orientation;
    float yawRadians = atan2(2.0 * (rotation.w * rotation.z + rotation.x * rotation.y), 1.0 - 2.0 * (rotation.y * rotation.y + rotation.z * rotation.z));
    float yawDegrees = yawRadians * (180.0 / M_PI);

    MovingAverageFilter* filterState = (hand->type == eLeapHandType_Left) ? &leftHandFilter : &rightHandFilter;

    if(hand->grab_strength > 0.95) {
      filterState->originX = palm_x;
      filterState->originY = palm_y;
      filterState->originZ = palm_z;
    }

    Hand_Status filteredStatus = applyMovingAverageFilter(filterState, palm_x, palm_y, palm_z, yawDegrees, thumb_index_distance);

    if(fabs(filteredStatus.newX - filterState->previousX) > position_change_threshold) {
        filterState->previousX = filteredStatus.newX;
        printX = filteredStatus.newX - filterState->originX;
    } else {
        printX = filterState->previousX - filterState->originX;
    }
    if(fabs(filteredStatus.newY - filterState->previousY) > position_change_threshold) {
        filterState->previousY = filteredStatus.newY;
        printY = filteredStatus.newY - filterState->originY;
    } else {
        printY = filterState->previousY - filterState->originY;
    }
    if(fabs(filteredStatus.newZ - filterState->previousZ) > position_change_threshold) {
        filterState->previousZ = filteredStatus.newZ;
        printZ = filteredStatus.newZ - filterState->originZ;
    } else {
        printZ = filterState->previousZ - filterState->originZ;
    }
    if(fabs(filteredStatus.newYaw - filterState->previousYaw) > yaw_change_threshold) {
        filterState->previousYaw = filteredStatus.newYaw;
        printYaw = filteredStatus.newYaw;
    } else {
        printYaw = filterState->previousYaw;
    }
    if(fabs(filteredStatus.newIndexThumbDistance - filterState->previousThumbIndexDistance) > thumb_index_change_threshold) {
        filterState->previousThumbIndexDistance = filteredStatus.newIndexThumbDistance;
        printIndexThumbDistance = filteredStatus.newIndexThumbDistance;
    } else {
        printIndexThumbDistance = filterState->previousThumbIndexDistance;
    }


    if(hand->type == eLeapHandType_Left){
        leftHandStatus.newX = printX;
        leftHandStatus.newY = printY;
        leftHandStatus.newZ = printZ;
        leftHandStatus.newYaw = printYaw;
        leftHandStatus.newIndexThumbDistance = printIndexThumbDistance;
        hasLeftHand = true;
    } else {
        rightHandStatus.newX = printX;
        rightHandStatus.newY = printY;
        rightHandStatus.newZ = printZ;
        rightHandStatus.newYaw = printYaw;
        rightHandStatus.newIndexThumbDistance = printIndexThumbDistance;
        hasRightHand = true;
    }
  }
  if(hasLeftHand && hasRightHand){
    printf("Left hand data (%f, %f, %f, %f, %f). Right hand data (%f, %f, %f, %f, %f).\n",
           leftHandStatus.newX, leftHandStatus.newY, leftHandStatus.newZ, leftHandStatus.newIndexThumbDistance, leftHandStatus.newYaw,
           rightHandStatus.newX, rightHandStatus.newY, rightHandStatus.newZ, rightHandStatus.newIndexThumbDistance, rightHandStatus.newYaw);
    fflush(stdout);
  }
} else if (!no_hand_message_printed) {
  printf("No hand detected.\n");
  fflush(stdout);
  no_hand_message_printed = 1;
}
}

// #define FILTER_SIZE 10
// #define YAW_CHANGE_THRESHOLD 1.0
// static float filter_x[FILTER_SIZE] = {0};
// static float filter_y[FILTER_SIZE] = {0};
// static float filter_z[FILTER_SIZE] = {0};
// static int filter_index = 0;
// static float previous_x = 0;
// static float previous_y = 0;
// static float previous_z = 0;
// static float previous_thumb_index_distance = 0;
// static float origin_x = 0, origin_y = 0, origin_z = 0;
// static int set_origin = 0;
// static int no_hand_message_printed = 0;

// static time_t lastPrintTime = 0;

// static int previous_fingers_touching = 0;
// static float previousYawDegrees = 0;
// static void OnFrame(const LEAP_TRACKING_EVENT *frame){
//     time_t now;
//     time(&now);
//     if (frame->nHands > 0) {
//       no_hand_message_printed = 0;
//       for (uint32_t h = 0; h < frame->nHands; h++) {
//           LEAP_HAND* hand = &frame->pHands[h];
//           LEAP_QUATERNION rotation = hand->palm.orientation;

//           float yawRadians = atan2(2.0 * (rotation.w * rotation.z + rotation.x * rotation.y), 1.0 - 2.0 * (rotation.y * rotation.y + rotation.z * rotation.z));

//           // Convert yaw to degrees
//           float yawDegrees = yawRadians * (180.0 / M_PI);

//           float filteredYawDegrees = applyMovingAverageFilter(yawDegrees);
//           float deltaYaw = fabs(filteredYawDegrees - previousYawDegrees); 
          
//           float palm_x = hand->palm.position.x;
//           float palm_y = hand->palm.position.y;
//           float palm_z = hand->palm.position.z;

//           float thumb_tip_x = hand->digits[0].distal.next_joint.x;
//           float thumb_tip_y = hand->digits[0].distal.next_joint.y;
//           float thumb_tip_z = hand->digits[0].distal.next_joint.z;
//           float index_tip_x = hand->digits[1].distal.next_joint.x;
//           float index_tip_y = hand->digits[1].distal.next_joint.y;
//           float index_tip_z = hand->digits[1].distal.next_joint.z;

//           // Calculate the distance from thumb tip and index tip to the palm
//           float thumb_to_palm_distance = sqrt(pow(thumb_tip_x - palm_x, 2) + pow(thumb_tip_y - palm_y, 2) + pow(thumb_tip_z - palm_z, 2));
//           float index_to_palm_distance = sqrt(pow(index_tip_x - palm_x, 2) + pow(index_tip_y - palm_y, 2) + pow(index_tip_z - palm_z, 2));
//           // Define a threshold for "obvious distance" from fingertip to palm
//           float distance_threshold = 70; // Adjust this value based on your application's needs

//           // Check if thumb and index fingertips are an obvious distance from the palm
//           int fingertips_extended = (thumb_to_palm_distance < distance_threshold) && (index_to_palm_distance < distance_threshold);

//           // Calculate distance between thumb and index fingertips
//           float thumb_index_distance = sqrt(pow(thumb_tip_x - index_tip_x, 2) + pow(thumb_tip_y - index_tip_y, 2) + pow(thumb_tip_z - index_tip_z, 2)) - 75;
//           // printf("thumb_index_distance: %f\n", thumb_index_distance);
//           // Check if thumb and index fingers are touching each other
//           int fingers_touching = (thumb_index_distance < 30) && fingertips_extended;

//           if (hand->grab_strength > 0.95) {
//               if (!fist_detected) {
//                 fist_detected = 1;
//                 last_fist_time = now;
//                 printf("Fist\n");
//               } else if (difftime(now, last_fist_time) > WAIT_SECONDS) {
//                 printf("Close\n");
//                 fist_detected = 0;
//               }
//               origin_x = palm_x;
//               origin_y = palm_y;
//               origin_z = palm_z;
//               set_origin = 1;
//               for (int i = 0; i < FILTER_SIZE; i++) {
//                   filter_x[i] = 0;
//                   filter_y[i] = 0;
//                   filter_z[i] = 0;
//               }
//               filter_index = 0; // Reset filter_index if necessary
//           } else {
//             fist_detected = 0;
//             if (set_origin && difftime(now, last_fist_time) > WAIT_SECONDS)
//               filter_x[filter_index] = hand->palm.position.x - origin_x;
//               filter_y[filter_index] = hand->palm.position.y - origin_y;
//               filter_z[filter_index] = hand->palm.position.z - origin_z;
//           }

//               // Calculate filtered position
//               float filtered_x = 0;
//               float filtered_y = 0;
//               float filtered_z = 0;
//               for (int i = 0; i < FILTER_SIZE; i++) {
//                   filtered_x += filter_x[i];
//                   filtered_y += filter_y[i];
//                   filtered_z += filter_z[i];
//               }
//               filtered_x /= FILTER_SIZE;
//               filtered_y /= FILTER_SIZE;
//               filtered_z /= FILTER_SIZE;

//               // Calculate changes in x, y, and z coordinates
//               float change_x = filtered_x - previous_x;
//               float change_y = filtered_y - previous_y;
//               float change_z = filtered_z - previous_z;

//               if ((fabs(change_x) > 2 && fabs(change_x) < 7) || 
//                   (fabs(change_y) > 2 && fabs(change_y) < 7) || 
//                   (fabs(change_z) > 2 && fabs(change_z) < 7) ||
//                   (fabs(thumb_index_distance - previous_thumb_index_distance) > 5) ||
//                   (deltaYaw > YAW_CHANGE_THRESHOLD)){
//                   printf("hand %d: x,y,z position: [%f, %f, %f], thumb_index_distance: %f, yaw angle: %f\n", 
//                   h, filtered_x, filtered_y, filtered_z, thumb_index_distance, filteredYawDegrees);

//                   previous_x = filtered_x;
//                   previous_y = filtered_y;
//                   previous_z = filtered_z;
//                   previous_thumb_index_distance = thumb_index_distance;
//                   previousYawDegrees = filteredYawDegrees;
//                   }

//               // Update filter index
//               filter_index = (filter_index + 1) % FILTER_SIZE;
//           fflush(stdout);
//       }
//     } else if (!no_hand_message_printed) {
//       printf("No hand detected.\n");
//       fflush(stdout);
//       no_hand_message_printed = 1;
//     }
// }



/** Callback for when an image is available. */
// static void OnImage(const LEAP_IMAGE_EVENT *imageEvent){
//     printf("Received image set for frame %lli with size %lli.\n",
//            (long long int)imageEvent->info.frame_id,
//            (long long int)imageEvent->image[0].properties.width*
//            (long long int)imageEvent->image[0].properties.height*2);
// }

int main(int argc, char** argv) {
  //Set callback function pointers
  ConnectionCallbacks.on_connection          = &OnConnect;
  ConnectionCallbacks.on_device_found        = &OnDevice;
  ConnectionCallbacks.on_frame               = &OnFrame;
  // ConnectionCallbacks.on_image               = &OnImage;

  LEAP_CONNECTION *connection = OpenConnection();
  LeapSetPolicyFlags(*connection, eLeapPolicyFlag_Images, 0);

  printf("Press Enter to exit program.\n");
  getchar();
  CloseConnection();
  DestroyConnection();
  return 0;
}
//End-of-Sample

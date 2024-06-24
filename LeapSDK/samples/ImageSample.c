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

/** Callback for when the connection opens. */
static void OnConnect(void){
  printf("Connected.\n");
}

/** Callback for when a device is found. */
static void OnDevice(const LEAP_DEVICE_INFO *props){
  printf("Found device %s.\n", props->serial);
}

/** Callback for when a frame of tracking data is available. */
// static void OnFrame(const LEAP_TRACKING_EVENT *frame){
//   printf("Frame %lli with %i hands.\n", (long long int)frame->info.frame_id, frame->nHands);
//   for(uint32_t h = 0; h < frame->nHands; h++){
//     LEAP_HAND* hand = &frame->pHands[h];
//     printf("    Hand id %i is a %s hand with position (%f, %f, %f).\n",
//                 hand->id,
//                 (hand->type == eLeapHandType_Left ? "left" : "right"),
//                 hand->palm.position.x,
//                 hand->palm.position.y,
//                 hand->palm.position.z);
//   }
// }
#define FILTER_SIZE 10
static void OnFrame(const LEAP_TRACKING_EVENT *frame){
    static float filter_x[FILTER_SIZE] = {0};
    static float filter_y[FILTER_SIZE] = {0};
    static float filter_z[FILTER_SIZE] = {0};
    static int filter_index = 0;
    static float previous_x = 0;
    static float previous_y = 0;
    static float previous_z = 0;
    static float origin_x = 0, origin_y = 0, origin_z = 0;
    static int set_origin = 0;
    static int no_hand_message_printed = 0;
    if (frame->nHands > 0) {
      no_hand_message_printed = 0;
      for (uint32_t h = 0; h < frame->nHands; h++) {
          LEAP_HAND* hand = &frame->pHands[h];
          if (hand->grab_strength > 0.95) {
              printf("Fist\n");
              origin_x = hand->palm.position.x;
              origin_y = hand->palm.position.y;
              origin_z = hand->palm.position.z;
              set_origin = 1;
              for (int i = 0; i < FILTER_SIZE; i++) {
                  filter_x[i] = 0;
                  filter_y[i] = 0;
                  filter_z[i] = 0;
              }
              filter_index = 0; // Reset filter_index if necessary
          } else if (set_origin) {
              filter_x[filter_index] = hand->palm.position.x - origin_x;
              filter_y[filter_index] = hand->palm.position.y - origin_y;
              filter_z[filter_index] = hand->palm.position.z - origin_z;
          } else {
              filter_x[filter_index] = hand->palm.position.x;
              filter_y[filter_index] = hand->palm.position.y;
              filter_z[filter_index] = hand->palm.position.z;
          }

              // Calculate filtered position
              float filtered_x = 0;
              float filtered_y = 0;
              float filtered_z = 0;
              for (int i = 0; i < FILTER_SIZE; i++) {
                  filtered_x += filter_x[i];
                  filtered_y += filter_y[i];
                  filtered_z += filter_z[i];
              }
              filtered_x /= FILTER_SIZE;
              filtered_y /= FILTER_SIZE;
              filtered_z /= FILTER_SIZE;

              // Calculate changes in x, y, and z coordinates
              float change_x = filtered_x - previous_x;
              float change_y = filtered_y - previous_y;
              float change_z = filtered_z - previous_z;

              if ((fabs(change_x) > 1 && fabs(change_x) < 7) || 
                  (fabs(change_y) > 1 && fabs(change_y) < 7) || 
                  (fabs(change_z) > 1 && fabs(change_z) < 7)) {
                  printf("x,y,z position: [%f, %f, %f]\n", filtered_x, filtered_y, filtered_z);
              }
              // printf("x,y,z position: [%f, %f, %f]\n", filtered_x, filtered_y, filtered_z);
              // Update the previous coordinates
              previous_x = filtered_x;
              previous_y = filtered_y;
              previous_z = filtered_z;

              // Update filter index
              filter_index = (filter_index + 1) % FILTER_SIZE;
          fflush(stdout);
      }
    } else if (!no_hand_message_printed) {
      printf("No hand detected.\n");
      fflush(stdout);
      no_hand_message_printed = 1;
    }
    // // test subject
    // static float previous_y = 0;
    // static float cumulative_change = 0;
    // static int no_hand_message_printed = 0;

    // if (frame->nHands > 0) {
    //   no_hand_message_printed = 0;
    //   for (uint32_t h = 0; h < frame->nHands; h++) {
    //     LEAP_HAND* hand = &frame->pHands[h];
    //     if (hand->grab_strength > 0.9) {
    //       printf("Fist\n");
    //     } else {
    //       float current_y = hand->palm.position.y;
    //       cumulative_change += current_y - previous_y;
    //       if (cumulative_change > 10) {
    //           printf("False\n");
    //           cumulative_change = 0;
    //       } else if (cumulative_change < -10) {
    //           printf("True\n");
    //           cumulative_change = 0;
    //       }
    //       previous_y = current_y;  // Update the previous y-coordinate
    //     }
    //     fflush(stdout);
    // }
    // } else if (!no_hand_message_printed) {
    //   printf("No hand detected.\n");
    //   fflush(stdout);
    //   no_hand_message_printed = 1;
    // }
}

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

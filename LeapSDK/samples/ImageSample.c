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

static void OnFrame(const LEAP_TRACKING_EVENT *frame){
    static time_t last_time = 0; // Static variable to store the last print time
    time_t current_time;
    time(&current_time);

    // Check if 5 seconds have passed since the last print
    if (difftime(current_time, last_time) >= 0.5) {
      // if (frame->nHands >0) {
      //   printf("Frame %lli with %i hands.\n", (long long int)frame->info.frame_id, frame->nHands);
      //   for (uint32_t h = 0; h < frame->nHands; h++) {
      //       LEAP_HAND* hand = &frame->pHands[h];
      //       printf("%s hand with position (%f, %f, %f).\n",
      //               (hand->type == eLeapHandType_Left ? "left" : "right"),
      //               hand->palm.position.x,
      //               hand->palm.position.y,
      //               hand->palm.position.z);
      //       if (hand->grab_strength > 0.9) {
      //         printf("Hand is closed\n");
      //       }
      //       if (hand->pinch_strength >0.7) {
      //         printf("Pinch gesture detected\n");
      //       }
      //   }
      // } else {
      //   printf("No hands detected.\n");
      // } 
      // test subject
      if (frame->nHands > 0) {
        printf("True\n");
        fflush(stdout);
      } else {
        printf("False\n");
        fflush(stdout);
      }
      last_time = current_time; // Update last_time to the current time after printing
    }
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

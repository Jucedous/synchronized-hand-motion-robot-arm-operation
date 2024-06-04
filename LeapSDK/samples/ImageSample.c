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
#include <netinet/in.h>
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

    if (difftime(current_time, last_time) >= 0.5) {
      if (frame->nHands >0) {
        printf("Frame %lli with %i hands.\n", (long long int)frame->info.frame_id, frame->nHands);
        for (uint32_t h = 0; h < frame->nHands; h++) {
            LEAP_HAND* hand = &frame->pHands[h];
            printf("%s hand with position (%f, %f, %f).\n",
                    (hand->type == eLeapHandType_Left ? "left" : "right"),
                    hand->palm.position.x,
                    hand->palm.position.y,
                    hand->palm.position.z);

            int clientSocket;
            struct sockaddr_in serverAddr;
            char buffer[1024];

            clientSocket = socket(PF_INET, SOCK_STREAM, 0);
            serverAddr.sin_family = AF_INET;
            serverAddr.sin_port = htons(7891);
            serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");

            connect(clientSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));

            sprintf(buffer, "%f", hand->palm.position.y);
            send(clientSocket, buffer, strlen(buffer), 0);
        }
      } else {
        printf("No hands detected.\n");
      }
        last_time = current_time;
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

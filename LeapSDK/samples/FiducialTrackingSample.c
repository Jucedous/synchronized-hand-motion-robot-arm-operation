/* Copyright (C) 2012-2024 Ultraleap Limited. All rights reserved.
 *
 * Use of this code is subject to the terms of the Ultraleap SDK agreement
 * available at https://central.leapmotion.com/agreements/SdkAgreement unless
 * Ultraleap has signed a separate license agreement with you or your
 * organisation.
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <time.h>
#include <math.h>
#include "LeapC.h"
#include "ExampleConnection.h"

/*
 This sample tracks the left index tip and a fiducial marker and tells you the
 distance between them. To run this sample, you should have an AprilTag fiducial
 marker that is IR reflective. The family and scale of the tag should be put in
 the hand tracker config as such:
 
  "fiducial_tracker": {
    "family": "Tag36h11",
    "size": 0.030000
  },
  
  Linux: /etc/ultraleap/hand_tracker_config.json
  MacOS: /etc/ultraleap/hand_tracker_config.json
  Windows: C:\ProgramData\Ultraleap\HandTracker\hand_tracker_config.json
*/

void clone_tracking_event(LEAP_TRACKING_EVENT* dst, const LEAP_TRACKING_EVENT* src)
{
  memcpy(&dst->info, &src->info, sizeof(LEAP_FRAME_HEADER));
  dst->tracking_frame_id = src->tracking_frame_id;
  dst->nHands = src->nHands;
  dst->framerate = src->framerate;
  memcpy(dst->pHands, src->pHands, src->nHands * sizeof(LEAP_HAND));
}

int main(int argc, char** argv) {

  LEAP_CONNECTION connection;

  LeapCreateConnection(NULL, &connection);
  LeapOpenConnection(connection);

  LEAP_CONNECTION_MESSAGE msg;
  unsigned int timeout_ms = 1000;
  eLeapRS res = eLeapRS_NotAvailable;

  LEAP_TRACKING_EVENT* latest_tracking_event = malloc(sizeof(LEAP_TRACKING_EVENT));
  latest_tracking_event->nHands = 0;
  latest_tracking_event->pHands = malloc(2 * sizeof(LEAP_HAND));
  
  do
  {
    LeapPollConnection(connection, timeout_ms, &msg);

    if (msg.type == eLeapEventType_Fiducial && latest_tracking_event->nHands > 0)
    {
      //if the last hand tracking event is older than 500ms, we won't try and compare them
      int64_t time_between_events = llabs(msg.fiducial_pose_event->timestamp - latest_tracking_event->info.timestamp);
      if (time_between_events < 500000)
      {
        LEAP_VECTOR index_tip_pos = latest_tracking_event->pHands[0].index.distal.next_joint;
        LEAP_VECTOR fiducial_pos = msg.fiducial_pose_event->translation;

        float distance = sqrt(powf(index_tip_pos.x - fiducial_pos.x, 2) +
                              powf(index_tip_pos.y - fiducial_pos.y, 2) +
                              powf(index_tip_pos.z - fiducial_pos.z, 2));

        printf("index tip is (%f, %f, %f) and fiducial is (%f, %f, %f), they are %f mm from each other \n", index_tip_pos.x, index_tip_pos.y, index_tip_pos.z, fiducial_pos.x, fiducial_pos.y, fiducial_pos.z, distance);
        fflush(stdout);
      }
    }

    //save the latest tracking event to compare with the next fiducial event
    if (msg.type == eLeapEventType_Tracking)
    {
      clone_tracking_event(latest_tracking_event, msg.tracking_event);
    }
    
  } while (res != eLeapRS_Success);
  
  return 0;
}
//End-of-Sample

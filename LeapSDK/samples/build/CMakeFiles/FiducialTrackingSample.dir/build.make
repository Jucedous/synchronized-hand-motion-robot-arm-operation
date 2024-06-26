# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.27

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/Cellar/cmake/3.27.6/bin/cmake

# The command to remove a file.
RM = /usr/local/Cellar/cmake/3.27.6/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build

# Include any dependencies generated for this target.
include CMakeFiles/FiducialTrackingSample.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/FiducialTrackingSample.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/FiducialTrackingSample.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/FiducialTrackingSample.dir/flags.make

CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o: CMakeFiles/FiducialTrackingSample.dir/flags.make
CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o: /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/FiducialTrackingSample.c
CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o: CMakeFiles/FiducialTrackingSample.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --progress-dir=/Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o"
	/Library/Developer/CommandLineTools/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o -MF CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o.d -o CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o -c /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/FiducialTrackingSample.c

CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Preprocessing C source to CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.i"
	/Library/Developer/CommandLineTools/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/FiducialTrackingSample.c > CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.i

CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green "Compiling C source to assembly CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.s"
	/Library/Developer/CommandLineTools/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/FiducialTrackingSample.c -o CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.s

# Object files for target FiducialTrackingSample
FiducialTrackingSample_OBJECTS = \
"CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o"

# External object files for target FiducialTrackingSample
FiducialTrackingSample_EXTERNAL_OBJECTS = \
"/Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/CMakeFiles/libExampleConnection.dir/ExampleConnection.c.o"

FiducialTrackingSample: CMakeFiles/FiducialTrackingSample.dir/FiducialTrackingSample.c.o
FiducialTrackingSample: CMakeFiles/libExampleConnection.dir/ExampleConnection.c.o
FiducialTrackingSample: CMakeFiles/FiducialTrackingSample.dir/build.make
FiducialTrackingSample: /Applications/Ultraleap\ Hand\ Tracking.app/Contents/LeapSDK/lib/libLeapC.5.dylib
FiducialTrackingSample: CMakeFiles/FiducialTrackingSample.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --green --bold --progress-dir=/Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable FiducialTrackingSample"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/FiducialTrackingSample.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/FiducialTrackingSample.dir/build: FiducialTrackingSample
.PHONY : CMakeFiles/FiducialTrackingSample.dir/build

CMakeFiles/FiducialTrackingSample.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/FiducialTrackingSample.dir/cmake_clean.cmake
.PHONY : CMakeFiles/FiducialTrackingSample.dir/clean

CMakeFiles/FiducialTrackingSample.dir/depend:
	cd /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build /Users/zhaozilin/Documents/GitHub/synchronized-hand-motion-robot-arm-operation/LeapSDK/samples/build/CMakeFiles/FiducialTrackingSample.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : CMakeFiles/FiducialTrackingSample.dir/depend


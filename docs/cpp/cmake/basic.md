# CMake Basic

> - [cmake-examples 01-basic](https://github.com/ttroy50/cmake-examples/tree/master/01-basic)

## CMakeLists.txt

```cmake
cmake_minium_required(VERSION 3.5)

project (<proj_name>)

# Modern CMake is NOT recommended to use a variable for sources.
# It is typical to directly declare the sources in the add_xxx function.
# This is particularly important for GLOB commands which may not alway show you the correct results if you add a new source file.
set(SOURCES
	src/...
)
file (GLOB SOURCES "src/*.cpp")

# This is just like the compiler with -I flag e.g. `-I/dir/include`
# Add dirs to be searched for header files during preprocessing.
tartget_include_directories(<target_proj>
	PRIVATE
		${PROJECT_SOURCE_DIR}/include
)

# The meaning of scopes are:
# 	PRIVATE: the dir is added to this target's include dirs.
# 	INTERFACE: the dir is added to include dirs for any targets that link this lib
# 	PUBLIC: included in this lib and also any targets that link this lib
# For public headers it is often a good idea to have your include folder be "namespaced" with sub-dirs.
# such as `#include "static/Hello.h"`
# There is less chance of header filename clashes.

# Create a library
# This will create a static lib with the name lib<lib_name>.a with the sources.
add_library(<lib_name> STATIC
	src/...
)
# This will create a shared lib with the name lib<lib_name>.so with the sources.
add_library(<lib_name> SHARED
	src/...
)
# Alias target, can reference the target using the alias name.
add_library(lib::name ALIAS <lib_name>)


# Link a library
target_link_libraries(<proj_name>
	PRIVATE
		<lib_name>
		# or use the alias name
		lib::namme
)

add_executable(${PROJECT_NAME} ${SOURCES})
```


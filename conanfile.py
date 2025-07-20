from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy
import os


class CStdConan(ConanFile):
    name = "c_std"
    version = "1.0"
    package_type = "application"

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "*.c", "*.h", "*/"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    
    # Sources are located in the same place as this recipe, copy them to the recipe
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        # Core dependencies identified from CMakeLists.txt
        # self.requires("openssl/[^1.1.1]")
        # self.requires("libpq/15.4")
        
        # Graphics library (raylib) - used on Linux
        if self.settings.os != "Windows":
            self.requires("raylib/4.5.0")



    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        
        tc = CMakeToolchain(self)
        # Set C standard as defined in original CMakeLists.txt
        tc.variables["CMAKE_C_STANDARD"] = "17"
        
        # Set compiler-specific flags
        if self.settings.compiler == "msvc":
            # MSVC-compatible flags
            tc.variables["CMAKE_C_FLAGS"] = "/W4 /O2"
        else:
            # GCC/Clang flags from original CMakeLists.txt
            tc.variables["CMAKE_C_FLAGS"] = "-g -O3 -march=native -funroll-loops -Wall -Wextra -pedantic -Wno-deprecated-declarations -s"
        
        # Platform-specific settings (only for MinGW/GCC on Windows)
        if self.settings.os == "Windows" and self.settings.compiler != "msvc":
            tc.variables["CMAKE_SHARED_LINKER_FLAGS"] = "-Wl,--enable-auto-import"
            tc.variables["CMAKE_EXE_LINKER_FLAGS"] = "-Wl,--enable-auto-import"
        
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.libs = ["c_std"]
        
        # Add system libraries based on platform
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "opengl32", "gdi32", "winmm", "ole32", "bthprops"
            ])
        else:
            self.cpp_info.system_libs.extend([
                "pthread", "dl", "m"
            ]) 
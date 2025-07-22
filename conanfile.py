from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, collect_libs
import os


class CStdConan(ConanFile):
    name = "c_std"
    version = "0.0.1-1"

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "*", "*.c", "*.h", "*/", "!build/"

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
        
        # Copy all header files from module directories
        modules = [
            "algorithm", "array", "audio", "bigfloat", "bigint", "bitset", "cli", 
            "concurrent", "config", "crypto", "csv", "database", "date", "deque", 
            "dir", "encoding", "evalexpr", "file_io", "fmt", "forward_list", "json", 
            "list", "log", "map", "matrix", "network", "numbers", "plot", 
            "priority_queue", "queue", "random", "regex", "secrets", "serial_port", 
            "span", "stack", "statistics", "string", "sysinfo", "time", "tuple", 
            "turtle", "unittest", "vector", "xml"
        ]
        
        # Copy header files from each module
        for module in modules:
            copy(self, "*.h", 
                 dst=os.path.join(self.package_folder, "include", module),
                 src=os.path.join(self.source_folder, module))
        
        # Copy main header if it exists
        copy(self, "*.h", 
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder)
        
        # Copy built libraries
        copy(self, "*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
        copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        
    def package_info(self):
        # Automatically collect all built libraries
        self.cpp_info.libs = collect_libs(self)
        
        # Add include directories
        self.cpp_info.includedirs = ["include"]
        
        # Add system libraries based on platform
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "opengl32", "gdi32", "winmm", "ole32", "bthprops"
            ])
        else:
            self.cpp_info.system_libs.extend([
                "pthread", "dl", "m"
            ]) 

    def deploy(self):
        # 1) include
        copy(self, "*.h*", src=self.source_folder,
             dst=os.path.join(self.deploy_folder, "include"),
             keep_path=True)          # keep_path=True is important to maintain the directory structure
        # 2) src（ keep the directory structure for source files）
        copy(self, "*.c*",   src=self.source_folder,
             dst=os.path.join(self.deploy_folder, "src"),
             keep_path=True)
        copy(self, "*.cpp*", src=self.source_folder,
             dst=os.path.join(self.deploy_folder, "src"),
             keep_path=True)


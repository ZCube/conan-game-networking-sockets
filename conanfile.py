from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os


class GameNetworkingSocketsConan(ConanFile):
    name = "game-networking-sockets"
    version = "1.1.0"
    description = "Reliable & unreliable messages over UDP"
    topics = ("conan", "udp", "network", "networking", "internet")
    url = "https://github.com/ZCube/conan-GameNetworkingSockets"
    homepage = "https://github.com/ValveSoftware/GameNetworkingSockets"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD 3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _commit = "85dc1cd4686355e4f8229d9c23607824f6a751ac"

    requires = (
        "openssl/1.1.1g",
        "grpc/1.29.1@zcube/stable",
    )

    def source(self):
        tools.get("https://github.com/ValveSoftware/GameNetworkingSockets/archive/v{}.tar.gz".format(self.version))
        os.rename("GameNetworkingSockets-" + self.version, self._source_subfolder)
        # tools.patch(self._source_subfolder, patch_file="conan.patch")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "OpenSSL::Crypto", "CONAN_PKG::openssl")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"), "${PROTOBUF_LIBRARIES}", "CONAN_PKG::grpc")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "check_symbol_exists(EVP_MD_CTX_free openssl/evp.h OPENSSL_NEW_ENOUGH)", "set(OPENSSL_NEW_ENOUGH ON)")

    def build(self):
        with tools.environment_append({"LD_LIBRARY_PATH": self.deps_cpp_info["grpc"].lib_paths}):
            cmake = CMake(self)
            cmake.definitions["Protobuf_USE_STATIC_LIBS"] = not self.options["grpc"].shared
            cmake.configure(build_folder=self._build_subfolder)
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.pdb", dst="lib", keep_path=False)
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
        # Copy correct lib
        if self.options.shared:
            libname = "GameNetworkingSockets"
        else:
            libname = "GameNetworkingSockets_s"
        if self.settings.compiler == "Visual Studio":
            self.copy("*{}{}.lib".format(os.sep, libname), dst="lib", keep_path=False)
        else:
            self.copy("*{}lib{}.dylib".format(os.sep, libname), dst="lib", keep_path=False, symlinks=True)
            self.copy("*{}lib{}.so".format(os.sep, libname), dst="lib", keep_path=False, symlinks=True)
            self.copy("*{}lib{}.a".format(os.sep, libname), dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["STEAMNETWORKINGSOCKETS_STATIC_LINK"]

        if os_info.is_linux:
            self.cpp_info.defines += ["POSIX", "LINUX"]
        elif os_info.is_macos:
            self.cpp_info.defines += ["POSIX", "OSX"]
        elif os_info.is_freebsd:
            self.cpp_info.defines += ["POSIX"]
        elif os_info.is_solaris:
            self.cpp_info.defines += ["POSIX"]
        elif os_info.is_windows:
            self.cpp_info.defines += ["WIN32"]

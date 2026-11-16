# DragonGL

DragonGL is the renderer fork used by Dragon Launcher. It is based on
[MobileGlues](https://github.com/MobileGL-Dev/MobileGlues), the OpenGL-to-OpenGL-ES
translation layer that lets Minecraft: Java Edition run on Android GLES drivers.

- Upstream: `MobileGL-Dev/MobileGlues`
- Base version: `2.0.0` (`f56af31d3e49`)
- License: LGPL-2.1-only (see `LICENSE`)
- Output: `libmobileglues.so`, packaged as an Android AAR
- Library name is kept as `libmobileglues.so` so existing launcher integration
  and `MG_DIR_PATH` configuration keep working.

## Why a fork

DragonGL is where Dragon Launcher-specific renderer work happens:

- reproducible arm64/armeabi-v7a/x86/x86_64 build from source instead of an
  opaque prebuilt AAR;
- stripped release binaries;
- launcher-side frame pacing and surface configuration;
- measured MobileGlues multi-draw / cache / extension tuning;
- Dragon Launcher defaults and diagnostics.

It is not a rewrite of MobileGlues. Compatibility fixes from upstream stay
available through the normal git history.

## Build

The build runs in GitHub Actions (`.github/workflows/dragongl.yml`) because the
Android NDK cannot run inside Termux.

Required submodules:

```sh
git submodule update --init --recursive -- \
  MobileGlues-cpp/3rdparty/glslang \
  MobileGlues-cpp/3rdparty/SPIRV-Cross \
  MobileGlues-cpp/3rdparty/xxhash \
  MobileGlues-cpp/include/ska
```

Local build shape:

```sh
cmake -S MobileGlues-cpp -B build \
  -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=android-21 \
  -DANDROID_STL=c++_static \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build --target mobileglues -j"$(nproc)"
```

`scripts/package-aar.sh` packages the result as an AAR. The launcher consumes
the AAR by replacing `app_pojavlauncher/libs/MobileGlues-release.aar`.

## License / source availability

DragonGL is distributed under LGPL-2.1-only, the same license as MobileGlues.
The complete corresponding source for every distributed AAR is this repository.
If you ship a modified DragonGL binary, publish the matching source and keep the
LGPL notice intact.

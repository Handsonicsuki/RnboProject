# Percussa RNBO SDK - GitHub Copilot Instructions

## Project Overview
This codebase enables building audio modules for Percussa SSP and XMX synthesizers from Max/MSP RNBO patches. The project wraps exported RNBO C++ code in JUCE VST3 plugins that integrate with Percussa's custom hardware interface.

## Architecture

### Core Components
- **RNBO Integration**: Exported Max/MSP RNBO patches become `RNBO::CoreObject` instances in C++
- **JUCE Wrapper**: VST3 plugins built with JUCE framework for cross-platform compatibility  
- **SSP/XMX API**: Custom hardware interface via `ssp::BaseProcessor` and Percussa SDK
- **Cross-compilation**: ARM builds for embedded Linux targets using custom CMake toolchains

### Key Directories
- `template/module/`: Template for new modules with `__MOD__` placeholders
- `modules/`: Individual module implementations (created from template)
- `modules/common/`: Shared SSP UI components and base classes
- `ssp-sdk/`: Percussa hardware abstraction layer
- `juce/`: JUCE framework submodule
- `scripts/create_module.sh`: Module scaffolding script

## Development Workflows

### Creating New Modules
```bash
# 1. Generate module template (4-char name required)
./scripts/create_module.sh TEST

# 2. Export RNBO patch to modules/TEST/rnbo-export/
# 3. Build using CMake presets or manual commands
```

### Build System
- **Local development**: `cmake ..` (native build for testing)
- **SSP target**: `cmake -DCMAKE_TOOLCHAIN_FILE=../xcSSP.cmake ..`
- **XMX target**: `cmake -DCMAKE_TOOLCHAIN_FILE=../xcXMX.cmake ..`
- **CMake Presets**: Use "local build", "ssp toolchain", or "xmx toolchain"

### Target-Specific Compilation
```cmake
# Conditional compilation flags in CMakeLists.txt
if(DEFINED ENV{TARGET_XMX} OR TARGET_XMX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DTARGET_XMX=1")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DTARGET_SSP=1")
endif()
```

## Code Patterns

### RNBO Parameter Integration
```cpp
// Auto-discover RNBO parameters and create JUCE parameter layout
RNBO::CoreObject rnboObj_;
unsigned nParams = rnboObj_.getNumParameters();
for (unsigned pn = 0; pn < nParams; pn++) {
    RNBO::ParameterInfo info;
    rnboObj_.getParameterInfo(pn, &info);
    if (info.visible) {
        // Create appropriate parameter type based on info.steps, info.enumValues
    }
}
```

### Audio Processing Pattern
```cpp
// Convert JUCE AudioBuffer to RNBO format and process
for (unsigned c = 0; c < rnbo_.nInputs_; c++) {
    for (unsigned i = 0; i < n; i++) {
        rnbo_.inputBuffers_[c][i] = buffer.getSample(c, i);
    }
}
rnbo_.patch_.process(rnbo_.inputBuffers_, rnbo_.nInputs_, 
                     rnbo_.outputBuffers_, rnbo_.nOutputs_, bufferSize_);
```

### SSP UI Integration
- Inherit from `ssp::BaseProcessor` not `AudioProcessor`
- Use `ssp::EditorHost` to wrap custom editors
- Conditional UI: `PluginEditor` for full SSP, `PluginMiniEditor` for compact/XMX
- Custom parameter types: `ssp::BaseFloatParameter`, `ssp::BaseBoolParameter`, etc.

## Build Dependencies

### Required Environment
- **macOS/Linux only** (Windows unsupported)
- **SSP Buildroot**: Download from Percussa, extract to `~/buildroot/`
- **Toolchain**: 
  - macOS: `brew install cmake git llvm pkg-config arm-linux-gnueabihf-binutils`
  - Linux: `apt install cmake git llvm clang g++-10-arm-linux-gnueabihf`

### Cross-compilation Setup
```bash
# Environment variables (optional, has defaults)
export SSP_BUILDROOT=$HOME/buildroot/arm-rockchip-linux-gnueabihf_sdk-buildroot
export TOOLSROOT=/opt/homebrew/opt/llvm/bin  # macOS M1
```

## Module Structure
```
modules/YOUR_MODULE/
├── CMakeLists.txt           # Build config (generated from template)
├── Source/
│   ├── PluginProcessor.cpp  # RNBO integration + SSP interface
│   ├── PluginEditor.cpp     # Full SSP UI (1920x1080)
│   ├── PluginMiniEditor.cpp # Compact UI (for XMX)
│   └── SSPApi.cpp          # Percussa hardware interface
└── rnbo-export/            # RNBO-generated C++ code
    ├── rnbo_source.cpp
    └── rnbo/RNBO.cpp
```

## Critical Integration Points
- **Template substitution**: `__MOD__` replaced with 4-character module name in CMakeLists.txt
- **RNBO export path**: Must be `modules/MODULE_NAME/rnbo-export/`
- **Bus configuration**: Auto-detected from RNBO patch input/output channels
- **Parameter mapping**: RNBO parameters automatically become JUCE parameters
- **UI scaling**: `COMPACT_UI_SCALE` preprocessor flag for different display densities

## Testing Strategy
- Build natively on macOS/Linux for development in DAW (loads as VST3)
- Use JUCE AudioPlugin Host for testing
- Cross-compile for final SSP/XMX deployment
- `INSTALL_PLUGIN=1` flag enables automatic plugin installation on macOS
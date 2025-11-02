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
- `template/module/`: Template for new modules with placeholder substitution system
- `modules/`: Individual module implementations (created from template)
- `modules/common/`: Shared SSP UI components and base classes
- `ssp-sdk/`: Percussa hardware abstraction layer
- `juce/`: JUCE framework submodule
- `scripts/`: Python tooling for module management and development workflow
  - `createModule.py`: Interactive module creation with validation
  - `removeModule.py`: Safe module removal with confirmation
  - `addDemo.py`: Create working demo module with real RNBO code
  - `check.py`: Environment validation and project status checker
  - `test/`: Development workflow automation scripts

## Development Workflows

### Environment Validation (Always Start Here)
```bash
# Check complete development environment before building
python3 scripts/check.py
```
This validates tools, toolchains, project structure, and existing modules.

### Creating New Modules
```bash
# Interactive mode (recommended for new users)
python3 scripts/createModule.py

# Non-interactive mode with all parameters
python3 scripts/createModule.py VERB --name "My Reverb" --description "Lush reverb effect" --author "Your Name" --email "your.email@example.com"

# Create demo module with working RNBO code
python3 scripts/addDemo.py
```

### Module Management
```bash
# List all existing modules
python3 scripts/removeModule.py --list

# Remove specific module with confirmation
python3 scripts/removeModule.py YOUR_MODULE

# Force removal without confirmation
python3 scripts/removeModule.py YOUR_MODULE --force

# Development workflow: create test modules
python3 scripts/test/test.py

# Clean up all test modules
python3 scripts/test/removeAll.py
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

### RNBO Integration Architecture
```cpp
// Template defines custom RNBO platform functions
namespace RNBO {
namespace Platform {
static void printMessage(const char* message) {}
static void printErrorMessage(const char* message) {}
}  // namespace Platform
}

// RNBO patch wrapper class
class RNBOPatch : public RNBO::__MOD__Rnbo<RNBO::MinimalEngine<>> {};

// Include generated RNBO code with diagnostic pragmas
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wswitch"
#pragma GCC diagnostic ignored "-Wunused-variable"
#include "../__MOD__-rnbo/__MOD__.cpp.h"
#pragma GCC diagnostic pop
```

### RNBO Parameter Integration
```cpp
// Template auto-discovers RNBO parameters and creates JUCE parameter layout
RNBO::__MOD__Rnbo<RNBO::MinimalEngine<>> patch;
patch.initialize();
unsigned nParams = patch.getNumParameters();
for (unsigned pn = 0; pn < nParams; pn++) {
    RNBO::ParameterInfo info;
    patch.getParameterInfo(pn, &info);
    if (info.visible) {
        String id = "param" + String(pn);
        String desc = info.displayName.length() > 0 ? info.displayName : patch.getParameterName(pn);
        
        if (info.enumValues) {
            // Create choice parameter for enums
            juce::StringArray choices;
            for (unsigned i = 0; i < info.steps; i++) {
                choices.add(info.enumValues[i]);
            }
            params.add(std::make_unique<ssp::BaseChoiceParameter>(id, desc, choices, info.initialValue));
        } else if (info.steps == 2) {
            // Create boolean parameter for 2-step parameters
            params.add(std::make_unique<ssp::BaseBoolParameter>(id, desc, info.initialValue > 0.5f));
        } else {
            // Create float parameter with optional step increment
            float inc = (info.steps > 2) ? (info.max - info.min) / (info.steps - 1) : 0.0f;
            params.add(std::make_unique<ssp::BaseFloatParameter>(id, desc, info.min, info.max, info.initialValue, inc));
        }
    }
}
```

### Audio Processing Pattern
```cpp
// Template uses RNBO::__MOD__Rnbo<RNBO::MinimalEngine<>> for processing
void processBlock(AudioSampleBuffer &buffer, MidiBuffer &) {
    // Convert JUCE AudioBuffer to RNBO format
    for (int c = 0; c < rnbo_.nInputs_; c++) {
        for (int i = 0; i < bufferSize_; i++) {
            rnbo_.inputBuffers_[c][i] = buffer.getSample(c, i);
        }
    }
    
    // Process through RNBO patch
    rnbo_.pPatch_->process(rnbo_.inputBuffers_, rnbo_.nInputs_, 
                          rnbo_.outputBuffers_, rnbo_.nOutputs_, bufferSize_);
    
    // Convert back to JUCE format
    for (int c = 0; c < rnbo_.nOutputs_; c++) {
        for (int i = 0; i < bufferSize_; i++) {
            buffer.setSample(c, i, rnbo_.outputBuffers_[c][i]);
        }
    }
}
```

### SSP UI Integration
- Inherit from `ssp::BaseProcessor` not `AudioProcessor`
- Use `ssp::EditorHost` to wrap custom editors
- Full editor: `ssp::MultiBarEditor` for complete SSP interface (1920x1080)
- Mini editor: `ssp::BaseMiniView` for compact/XMX display
- Custom parameter types: `ssp::BaseFloatParameter`, `ssp::BaseBoolParameter`, `ssp::BaseChoiceParameter`
- Template automatically handles bus configuration from RNBO patch I/O

## Build Dependencies

### Required Environment
- **macOS/Linux only** (Windows unsupported)
- **SSP Buildroot**: Download from Percussa, extract to `~/buildroot/`
- **Toolchain**: 
  - macOS: `brew install cmake git llvm pkg-config arm-linux-gnueabihf-binutils`
  - Linux: `apt install cmake git llvm clang g++-10-arm-linux-gnueabihf`

### Cross-compilation Setup
```bash
# Environment variables (recommended)
export SSP_BUILDROOT="$HOME/buildroot/arm-rockchip-linux-gnueabihf_sdk-buildroot"
export XMX_BUILDROOT="$HOME/buildroot/aarch64-rockchip-linux-gnu_sdk-buildroot"  # Optional for XMX
export TOOLSROOT="/opt/homebrew/opt/llvm/bin"  # macOS M1, auto-detected if not set

# Verify environment
python3 scripts/check.py
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
└── YOUR_MODULE-rnbo/        # RNBO-generated C++ code
    ├── description.json     # RNBO patch metadata
    ├── YOUR_PATCH.cpp.h     # Generated C++ code
    └── dependencies.json    # RNBO dependencies
```

## Critical Integration Points
- **Template substitution**: Multiple placeholders replaced during module creation
  - `__MOD__`: 4-character module ID (uppercase, starts with letter)  
  - `__NAME__`: Human-readable module name
  - `__DESCRIPTION__`: Module description
  - `__BRAND__`: Brand/company name
  - `__AUTHOR__`: Author name
  - `__EMAIL__`: Contact email
  - `__URL__`: Project/company URL
- **RNBO export path**: Must be `modules/MODULE_NAME/MODULE_NAME-rnbo/`
- **Bus configuration**: Auto-detected from RNBO patch input/output channels
- **Parameter mapping**: RNBO parameters automatically become JUCE parameters
- **UI scaling**: `COMPACT_UI_SCALE` preprocessor flag for different display densities

## Testing Strategy
- Build natively on macOS/Linux for development in DAW (loads as VST3)
- Use JUCE AudioPlugin Host for testing
- Cross-compile for final SSP/XMX deployment
- `INSTALL_PLUGIN=1` flag enables automatic plugin installation on macOS
- Use `python3 scripts/addDemo.py` to create working example module
- Environment validation with `python3 scripts/check.py` before building

## Python Tooling Context
The project uses a comprehensive Python script ecosystem for module management:

### createModule.py Features
- Interactive and non-interactive modes
- 7-placeholder template substitution system
- Module ID validation (4 chars, uppercase, starts with letter)
- Cross-platform compatibility (Windows paths handled)
- Automatic CMakeLists.txt updates
- Creates proper RNBO export directory structure

### removeModule.py Features  
- Safe module removal with confirmation prompts
- Bulk module removal capability
- CMakeLists.txt cleanup
- Force mode for scripted workflows
- Directory validation before removal

### addDemo.py Features
- Creates DEMO module with real RNBO code
- Copies from template/Demo/ to modules/DEMO/
- Provides working example for new users
- Includes proper build instructions
- Demo implements 4-channel mixer with gain controls per channel
- RNBO description.json contains complete parameter and I/O metadata

### check.py Features
- Validates complete development environment
- Checks tools: cmake, git, python, clang, clang++
- Verifies environment variables (SSP_BUILDROOT, XMX_BUILDROOT)
- Analyzes existing modules and their completion status
- Provides specific next steps based on current state
- Cross-platform tool detection (macOS homebrew paths, Linux packages)

### Development Workflow Scripts
- `scripts/test/test.py`: Creates TEST and VERB modules for development
- `scripts/test/removeAll.py`: Bulk cleanup with safety confirmations
- All scripts use Windows-compatible paths and avoid Unicode characters
- Consistent error handling and user feedback
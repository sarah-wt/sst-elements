// Copyright 2009-2021 NTESS. Under the terms
// of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2021, NTESS
// All rights reserved.
//
// Portions are copyright of other developers:
// See the file CONTRIBUTORS.TXT in the top level directory
// the distribution for more information.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.

#include <stdint.h>
#include "util.h"

using namespace std;

namespace SST {
namespace BalarComponent {
    string* gpu_api_to_string(enum GpuApi_t api) {
        string *str;
        switch (api) {
            case GPU_REG_FAT_BINARY:
                str = new string("GPU_REG_FAT_BINARY");
                break;
            case GPU_REG_FAT_BINARY_RET:
                str = new string("GPU_REG_FAT_BINARY_RET");
                break;
            case GPU_REG_FUNCTION:
                str = new string("GPU_REG_FUNCTION");
                break;
            case GPU_REG_FUNCTION_RET:
                str = new string("GPU_REG_FUNCTION_RET");
                break;
            case GPU_MEMCPY:
                str = new string("GPU_MEMCPY");
                break;
            case GPU_MEMCPY_RET:
                str = new string("GPU_MEMCPY_RET");
                break;
            case GPU_CONFIG_CALL:
                str = new string("GPU_CONFIG_CALL");
                break;
            case GPU_CONFIG_CALL_RET:
                str = new string("GPU_CONFIG_CALL_RET");
                break;
            case GPU_SET_ARG:
                str = new string("GPU_SET_ARG");
                break;
            case GPU_SET_ARG_RET:
                str = new string("GPU_SET_ARG_RET");
                break;
            case GPU_LAUNCH:
                str = new string("GPU_LAUNCH");
                break;
            case GPU_LAUNCH_RET:
                str = new string("GPU_LAUNCH_RET");
                break;
            case GPU_FREE:
                str = new string("GPU_FREE");
                break;
            case GPU_FREE_RET:
                str = new string("GPU_FREE_RET");
                break;
            case GPU_GET_LAST_ERROR:
                str = new string("GPU_GET_LAST_ERROR");
                break;
            case GPU_GET_LAST_ERROR_RET:
                str = new string("GPU_GET_LAST_ERROR_RET");
                break;
            case GPU_MALLOC:
                str = new string("GPU_MALLOC");
                break;
            case GPU_MALLOC_RET:
                str = new string("GPU_MALLOC_RET");
                break;
            case GPU_REG_VAR:
                str = new string("GPU_REG_VAR");
                break;
            case GPU_REG_VAR_RET:
                str = new string("GPU_REG_VAR_RET");
                break;
            case GPU_MAX_BLOCK:
                str = new string("GPU_MAX_BLOCK");
                break;
            case GPU_MAX_BLOCK_RET:
                str = new string("GPU_MAX_BLOCK_RET");
                break;
            default:
                str = new string("Unknown cuda calls");
                break;
        }
        return str;
    }

}
}
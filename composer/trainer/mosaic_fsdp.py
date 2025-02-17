# Copyright 2022 MosaicML Composer authors
# SPDX-License-Identifier: Apache-2.0

# Released under BSD 3-Clause License,
# Copyright (c) Facebook, Inc. and its affiliates.

"""Monkey patch FSDPs _auto_wrap to enable module_kwargs and custom process_group cache and ChunkShardingSpec to enable sharding over all gpus."""

import torch
from packaging import version
from torch.distributed._shard.sharding_spec import ChunkShardingSpec
from torch.distributed.fsdp import FullyShardedDataParallel

from composer.trainer.mosaic_fsdp_utils import build_metadata, custom_auto_wrap_t1p13p1, shard


def patch_pytorch():
    """Monkey patches pytorch functions based on pytorch version."""
    if version.parse(torch.__version__) < version.parse('1.13.1'):
        raise NotImplementedError(f'Not supported for torch < 1.13.1')

    elif version.parse(torch.__version__) < version.parse('2.0.0'):
        # FullyShardedDataParallel monkey path for torch < 2.0 ie torch == 1.13.1

        # monkey patch _auto_wrap with _custom_auto_wrap fn
        FullyShardedDataParallel._auto_wrap = custom_auto_wrap_t1p13p1  # type: ignore

    elif version.parse(torch.__version__) < version.parse('2.0.1'):
        raise NotImplementedError(f'Not supported for torch == 2.0.0')

    elif version.parse(torch.__version__) == version.parse('2.0.1'):
        # Monkey patch for torch == 2.0.1

        # Monkey patch __init__ where __init__ calls the custom _auto_wrap fn
        from composer.trainer.mosaic_fsdp_utils import init_fn_t2p0p1
        FullyShardedDataParallel.__init__ = init_fn_t2p0p1

        # Monkey patch sharding method
        ChunkShardingSpec.build_metadata = build_metadata
        ChunkShardingSpec.shard = shard

    elif version.parse(torch.__version__) < version.parse('2.2.0'):
        # Monkey path for torch < 2.2.0 ie torch == 2.1.0

        # Monkey patch sharding method
        ChunkShardingSpec.build_metadata = build_metadata
        ChunkShardingSpec.shard = shard

    elif version.parse(torch.__version__) >= version.parse('2.2.0'):
        raise NotImplementedError(f'Not supported for torch >= 2.2.0')

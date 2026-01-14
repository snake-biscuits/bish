from __future__ import annotations
import io

from breki.binary import read_struct


class Statistics:
    num_instructions: int
    num_temp_registers: int
    num_defines: int
    ...

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> Statistics:
        assert len(raw_chunk) == 148, f"unexpected size: {len(raw_chunk)} bytes"
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Statistics:
        out = cls()
        out.num_instructions = read_struct(stream, "I")
        out.num_temp_registers = read_struct(stream, "I")
        out.num_defines = read_struct(stream, "I")
        out.num_declarations = read_struct(stream, "I")
        out.num_floats = read_struct(stream, "I")
        out.num_ints = read_struct(stream, "I")
        out.num_uints = read_struct(stream, "I")
        out.num_static_flow_controls = read_struct(stream, "I")
        out.num_dynamic_flow_controls = read_struct(stream, "I")
        out.unknown_1 = read_struct(stream, "I")
        out.num_temp_arrays = read_struct(stream, "I")
        out.num_arrays = read_struct(stream, "I")
        out.num_cuts = read_struct(stream, "I")
        out.num_emits = read_struct(stream, "I")
        out.num_texture_normals = read_struct(stream, "I")
        out.num_texture_loads = read_struct(stream, "I")
        out.num_texture_comparisons = read_struct(stream, "I")
        out.num_texture_biases = read_struct(stream, "I")
        out.num_texture_gradients = read_struct(stream, "I")
        out.num_movs = read_struct(stream, "I")
        out.num_movcs = read_struct(stream, "I")
        out.num_conversions = read_struct(stream, "I")
        out.unknown_2 = read_struct(stream, "I")
        out.geo_shader_input_primitives = read_struct(stream, "I")
        out.geo_shader_primitive_topology = read_struct(stream, "I")
        out.geo_shader_max_vertices = read_struct(stream, "I")
        out.unknown_3 = read_struct(stream, "I")
        out.unknown_4 = read_struct(stream, "I")
        out.is_sample_frequency_shader = [False, True][read_struct(stream, "I")]
        return out

#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'tracer0tong'

import os, sys
from optparse import OptionParser
from pprint import pprint

from construct import *

class InvalidInstructionException(Exception):
    pass

InstructionSet = {
    0x00: ['nop','10x'],
    0x01: ['mov','12x'],
    0x02: ['move/from16','22x'],
    0x03: ['move/16','32x'],
    0x04: ['mov-wide','12x'],
    0x05: ['move-wide/from16','22x'],
    0x06: ['move-wide/16','32x'],
    0x07: ['mov-object','12x'],
    0x08: ['move-object/from16','22x'],
    0x09: ['move-object/16','32x'],
    0x0a: ['move-result','11x'],
    0x0b: ['move-result-wide','11x'],
    0x0c: ['move-result-object','11x'],
    0x0d: ['move-exception','11x'],
    0x0e: ['return-void','10x'],
    0x0f: ['return','11x'],
    0x10: ['return-wide','11x'],
    0x11: ['return-object','11x'],
    0x12: ['const/4','11n'],
    0x13: ['const/16','21s'],
    0x14: ['const','31i'],
    0x15: ['const/high16','21h'],
    0x16: ['const-wide/16','21s'],
    0x17: ['const-wide/32','31i'],
    0x18: ['const-wide','51l'],
    0x19: ['const-wide/high16','w21h'],
    0x1a: ['const-string','s21c'],
    0x1b: ['const-string/jumbo','s31c'],
    0x1c: ['const-class','t21c'],
    0x1d: ['monitor-enter','11x'],
    0x1e: ['monitor-exit','11x'],
    0x1f: ['check-cast','t21c'],
    0x20: ['instance-of','t22c'],
    0x21: ['array-length','12x'],
    0x22: ['new-instance','t21c'],
    0x23: ['new-array','t22c'],
    0x24: ['filled-new-array','t35c'],
    0x25: ['filled-new-array/range','t3rc'],
    0x26: ['fill-array-data','31t'],
    0x27: ['throw','11x'],
    0x28: ['goto','10t'],
    0x29: ['goto/16','20t'],
    0x2a: ['goto/32','30t'],
    0x2b: ['packed-switch','31t'],
    0x2c: ['sparse-switch','31t'],
    0x2d: ['cmpl-float','23x'],
    0x2e: ['cmpg-float','23x'],
    0x2f: ['cmpl-double','23x'],
    0x30: ['cmpg-double','23x'],
    0x31: ['cmp-long','23x'],
    0x32: ['if-eq','22t'],
    0x33: ['if-ne','22t'],
    0x34: ['if-lt','22t'],
    0x35: ['if-ge','22t'],
    0x36: ['if-gt','22t'],
    0x37: ['if-le','22t'],
    0x38: ['if-eqz','21t'],
    0x39: ['if-nez','21t'],
    0x3a: ['if-ltz','21t'],
    0x3b: ['if-gez','21t'],
    0x3c: ['if-gtz','21t'],
    0x3d: ['if-lez','21t'],
    #----------------------------
    #(unused)
    #----------------------------
    0x44: ['aget','23x'],
    0x45: ['aget-wide','23x'],
    0x46: ['aget-object','23x'],
    0x47: ['aget-boolean','23x'],
    0x48: ['aget-byte','23x'],
    0x49: ['aget-char','23x'],
    0x4a: ['aget-short','23x'],
    0x4b: ['aput','23x'],
    0x4c: ['aput-wide','23x'],
    0x4d: ['aput-object','23x'],
    0x4e: ['aput-boolean','23x'],
    0x4f: ['aput-byte','23x'],
    0x50: ['aput-char','23x'],
    0x51: ['aput-short','23x'],
    0x52: ['iget','f22c'],
    0x53: ['iget-wide','f22c'],
    0x54: ['iget-object','f22c'],
    0x55: ['iget-boolean','f22c'],
    0x56: ['iget-byte','f22c'],
    0x57: ['iget-char','f22c'],
    0x58: ['iget-short','f22c'],
    0x59: ['iput','f22c'],
    0x5a: ['iput-wide','f22c'],
    0x5b: ['iput-object','f22c'],
    0x5c: ['iput-boolean','f22c'],
    0x5d: ['iput-byte','f22c'],
    0x5e: ['iput-char','f22c'],
    0x5f: ['iput-short','f22c'],
    0x60: ['sget','f21c'],
    0x61: ['sget-wide','f21c'],
    0x62: ['sget-object','f21c'],
    0x63: ['sget-boolean','f21c'],
    0x64: ['sget-byte','f21c'],
    0x65: ['sget-char','f21c'],
    0x66: ['sget-short','f21c'],
    0x67: ['sput','f21c'],
    0x68: ['sput-wide','f21c'],
    0x69: ['sput-object','f21c'],
    0x6a: ['sput-boolean','f21c'],
    0x6b: ['sput-byte','f21c'],
    0x6c: ['sput-char','f21c'],
    0x6d: ['sput-short','f21c'],
    0x6e: ['invoke-virtual','i35c'],
    0x6f: ['invoke-super','i35c'],
    0x70: ['invoke-direct','i35c'],
    0x71: ['invoke-static','i35c'],
    0x72: ['invoke-interface','i35c'],
    #----------------------------
    #(unused)
    #----------------------------
    0x74: ['invoke-virtual/range','i3rc'],
    0x75: ['invoke-super/range','i3rc'],
    0x76: ['invoke-direct/range','i3rc'],
    0x77: ['invoke-static/range','i3rc'],
    0x78: ['invoke-interface/range','i3rc'],
    #----------------------------
    #(unused)
    #----------------------------
    0x7b: ['neg-int','12x'],
    0x7c: ['not-int','12x'],
    0x7d: ['neg-long','12x'],
    0x7e: ['not-long','12x'],
    0x7f: ['neg-float','12x'],
    0x80: ['neg-double','12x'],
    0x81: ['int-to-long','12x'],
    0x82: ['int-to-float','12x'],
    0x83: ['int-to-double','12x'],
    0x84: ['long-to-int','12x'],
    0x85: ['long-to-float','12x'],
    0x86: ['long-to-double','12x'],
    0x87: ['float-to-int','12x'],
    0x88: ['float-to-long','12x'],
    0x89: ['float-to-double','12x'],
    0x8a: ['double-to-int','12x'],
    0x8b: ['double-to-long','12x'],
    0x8c: ['double-to-float','12x'],
    0x8d: ['int-to-byte','12x'],
    0x8e: ['int-to-char','12x'],
    0x8f: ['int-to-short','12x'],
    0x90: ['add-int','23x'],
    0x91: ['sub-int','23x'],
    0x92: ['mul-int','23x'],
    0x93: ['div-int','23x'],
    0x94: ['rem-int','23x'],
    0x95: ['and-int','23x'],
    0x96: ['or-int','23x'],
    0x97: ['xor-int','23x'],
    0x98: ['shl-int','23x'],
    0x99: ['shr-int','23x'],
    0x9a: ['ushr-int','23x'],
    0x9b: ['add-long','23x'],
    0x9c: ['sub-long','23x'],
    0x9d: ['mul-long','23x'],
    0x9e: ['div-long','23x'],
    0x9f: ['rem-long','23x'],
    0xa0: ['and-long','23x'],
    0xa1: ['or-long','23x'],
    0xa2: ['xor-long','23x'],
    0xa3: ['shl-long','23x'],
    0xa4: ['shr-long','23x'],
    0xa5: ['ushr-long','23x'],
    0xa6: ['add-float','23x'],
    0xa7: ['sub-float','23x'],
    0xa8: ['mul-float','23x'],
    0xa9: ['div-float','23x'],
    0xaa: ['rem-float','23x'],
    0xab: ['add-double','23x'],
    0xac: ['sub-double','23x'],
    0xad: ['mul-double','23x'],
    0xae: ['div-double','23x'],
    0xaf: ['rem-double','23x'],
    0xb0: ['add-int/2addr','12x'],
    0xb1: ['sub-int/2addr','12x'],
    0xb2: ['mul-int/2addr','12x'],
    0xb3: ['div-int/2addr','12x'],
    0xb4: ['rem-int/2addr','12x'],
    0xb5: ['and-int/2addr','12x'],
    0xb6: ['or-int/2addr','12x'],
    0xb7: ['xor-int/2addr','12x'],
    0xb8: ['shl-int/2addr','12x'],
    0xb9: ['shr-int/2addr','12x'],
    0xba: ['ushr-int/2addr','12x'],
    0xbb: ['add-long/2addr','12x'],
    0xbc: ['sub-long/2addr','12x'],
    0xbd: ['mul-long/2addr','12x'],
    0xbe: ['div-long/2addr','12x'],
    0xbf: ['rem-long/2addr','12x'],
    0xc0: ['and-long/2addr','12x'],
    0xc1: ['or-long/2addr','12x'],
    0xc2: ['xor-long/2addr','12x'],
    0xc3: ['shl-long/2addr','12x'],
    0xc4: ['shr-long/2addr','12x'],
    0xc5: ['ushr-long/2addr','12x'],
    0xc6: ['add-float/2addr','12x'],
    0xc7: ['sub-float/2addr','12x'],
    0xc8: ['mul-float/2addr','12x'],
    0xc9: ['div-float/2addr','12x'],
    0xca: ['rem-float/2addr','12x'],
    0xcb: ['add-double/2addr','12x'],
    0xcc: ['sub-double/2addr','12x'],
    0xcd: ['mul-double/2addr','12x'],
    0xce: ['div-double/2addr','12x'],
    0xcf: ['rem-double/2addr','12x'],
    0xd0: ['add-int/lit16','22s'],
    0xd1: ['rsub-int','22s'],
    0xd2: ['mul-int/lit16','22s'],
    0xd3: ['div-int/lit16','22s'],
    0xd4: ['rem-int/lit16','22s'],
    0xd5: ['and-int/lit16','22s'],
    0xd6: ['or-int/lit16','22s'],
    0xd7: ['xor-int/lit16','22s'],
    0xd8: ['add-int/lit8','22b'],
    0xd9: ['rsub-int/lit8','22b'],
    0xda: ['mul-int/lit8','22b'],
    0xdb: ['div-int/lit8','22b'],
    0xdc: ['rem-int/lit8','22b'],
    0xdd: ['and-int/lit8','22b'],
    0xde: ['or-int/lit8','22b'],
    0xdf: ['xor-int/lit8','22b'],
    0xe0: ['shl-int/lit8','22b'],
    0xe1: ['shr-int/lit8','22b'],
    0xe2: ['ushr-int/lit8','22b']
    #-----------------------------
    #(unused)
    #-----------------------------
}

class DexDecompiler:
    #DexFile = None
    RawBytes = None
    Listing = None
    OneWordInstructions = []
    TwoWordInstructions = []
    ThreeWordInstructions = []
    FiveWordInstructions = []
    pos = 0
    op_cnt = 0x0000

    PackedSwitchPayload = Struct('psp',Magic(b'\x00\x01'),
                                 ULInt16('sz'),
                                 SLInt32('first_key'),
                                 Array(lambda ctx: ctx.sz,SLInt32('targets'))
    )

    SparseSwitchPayload = Struct('ssp',Magic(b'\x00\x02'),
                                 ULInt16('sz'),
                                 Array(lambda ctx: ctx.sz,SLInt32('keys')),
                                 Array(lambda ctx: ctx.sz,SLInt32('targets'))
    )

    FillArrayDataPayload = Struct('fadp',Magic(b'\x00\x03'),
                                 ULInt16('element_width'),
                                 ULInt32('sz'),
                                 Array(lambda ctx: ctx.sz,ULInt8('values'))
    )

    #AA|op
    args_10t = BitStruct(None,
                          Octet('op'),
                          BitField('AA',8,signed=True)
    )

    #00|op AAAA
    args_20t = BitStruct(None,
                         Octet('op'),
                         Const(Octet(None),0),
                         BitField('AAAA',16,signed=True,swapped=True)
    )

    #00|op AAAAlo AAAAhi
    args_30t = BitStruct(None,
                         Octet('op'),
                         Const(Octet(None),0),
                         BitField('AAAAAAAA',32,bytesize=8,signed=True,swapped=True),
    )

    #AA|op BBBBlo BBBBhi
    args_31t = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBBBBBB',32,bytesize=8,signed=True,swapped=True),
    )

    #AA|op BBBBlo BBBBhi
    args_31c = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBBBBBB',32,bytesize=8,swapped=True),
    )

    #AA|op BBBBlo BBBBhi
    args_31i = args_31t

    #B|A|op
    args_11n = BitStruct(None,
                         Octet('op'),
                         Nibble('B'),
                         Nibble('A')
    )

    #AA|op
    args_11x = BitStruct(None,
                         Octet('op'),
                         Octet('AA')
    )

    #B|A|op
    args_12x = args_11n

    #AA|op CC|BB
    args_22b = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         Octet('BB'),
                         BitField('CC',8,signed=True)
    )

    #B|A|op CCCC
    args_22t = BitStruct(None,
                         Octet('op'),
                         Nibble('B'),
                         Nibble('A'),
                         BitField('CCCC',16,signed=True,swapped=True)
    )

    args_22s = args_22t

    #B|A|op CCCC
    args_22c = BitStruct(None,
                         Octet('op'),
                         Nibble('B'),
                         Nibble('A'),
                         BitField('CCCC',16,swapped=True)
    )

    #AA|op BBBB
    args_22x = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBB',16,swapped=True)
    )

    args_21c = args_22x

    args_21t = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBB',16,signed=True,swapped=True)
    )

    args_21s = args_21t
    args_21h = args_21t

    #AA|op CC|BB
    args_23x = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         Octet('BB'),
                         Octet('CC')
    )

    #ØØ|op AAAA BBBB
    args_32x = BitStruct(None,
                         Octet('op'),
                         Const(Octet(None),0),
                         BitField('AAAA',16,swapped=True),
                         BitField('BBBB',16,swapped=True)
    )

    #A|G|op BBBB F|E|D|C
    args_35c = BitStruct(None,
                         Octet('op'),
                         Nibble('A'),
                         Nibble('G'),
                         BitField('BBBB',16,swapped=True),
                         Nibble('D'),
                         Nibble('C'),
                         Nibble('F'),
                         Nibble('E')
    )

    # AA|op BBBB CCCC
    args_3rc = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBB',16,swapped=True),
                         BitField('CCCC',16,swapped=True),
    )

    args_51l = BitStruct(None,
                         Octet('op'),
                         Octet('AA'),
                         BitField('BBBBBBBBBBBBBBBB',32,bytesize=8,swapped=True)
    )

    i32f32 = Union(None,LFloat32('f32'),SLInt32('i32'))

    def __init__(self):
        self.RawBytes = []
        self.Listing = []
        self.CalledMethods = []
        self.OneWordInstructions = [0x00,0x01,0x04,0x07]
        self.OneWordInstructions.extend(range(0x0a,0x13))
        self.OneWordInstructions.extend([0x1d,0x1e,0x21,0x27,0x28])
        self.OneWordInstructions.extend(range(0x3e,0x44))
        self.OneWordInstructions.extend([0x73,0x79,0x7a])
        self.OneWordInstructions.extend(range(0x7b,0x90))
        self.OneWordInstructions.extend(range(0xb0,0xd0))
        self.OneWordInstructions.extend(range(0xe3,0x100))
        self.TwoWordInstructions = [0x02,0x05,0x08,0x13,0x15,0x16,0x19,0x1a,0x1c,0x1f,0x20,0x22,0x23,0x29]
        self.TwoWordInstructions.extend(range(0x2d,0x3e))
        self.TwoWordInstructions.extend(range(0x44,0x6e))
        self.TwoWordInstructions.extend(range(0x90,0xb0))
        self.TwoWordInstructions.extend(range(0xd0,0xe3))
        self.ThreeWordInstructions = [0x03,0x06,0x09,0x14,0x17,0x1b,0x24,0x25,0x26,0x2a,0x2b,0x2c]
        self.ThreeWordInstructions.extend(range(0x6e,0x73))
        self.ThreeWordInstructions.extend(range(0x74,0x79))
        self.FiveWordInstructions = [0x18]

    def load_bytearray(self, rawbytes):
        self.RawBytes = rawbytes

    def extract_instruction(self):
        try:
            operation = []
            sw_op = self.RawBytes[self.pos]
            if (sw_op == 0x00) and self.RawBytes[self.pos+1] == 0x01:
                psp = self.PackedSwitchPayload.parse(self.RawBytes[self.pos:])
                self.pos += (psp['sz']*2 + 4) * 2
                operation = psp.__dict__
            elif (sw_op == 0x00) and self.RawBytes[self.pos+1] == 0x02:
                ssp = self.SparseSwitchPayload.parse(self.RawBytes[self.pos:])
                self.pos += (ssp['sz'] * 4 + 2) * 2
                operation = ssp.__dict__
            elif (sw_op == 0x00) and self.RawBytes[self.pos+1] == 0x03:
                fadp = self.FillArrayDataPayload.parse(self.RawBytes[self.pos:])
                self.pos += int((fadp['sz'] * fadp['element_width'] + 1)/2 + 4)*2
                operation = fadp.__dict__
            else:
                if sw_op in self.OneWordInstructions:
                    operation = self.RawBytes[self.pos:self.pos + 2]
                    self.pos += 2
                elif sw_op in self.TwoWordInstructions:
                    operation = self.RawBytes[self.pos:self.pos + 4]
                    self.pos += 4
                elif sw_op in self.ThreeWordInstructions:
                    operation = self.RawBytes[self.pos:self.pos + 6]
                    self.pos += 6
                elif sw_op in self.FiveWordInstructions:
                    operation = self.RawBytes[self.pos:self.pos + 10]
                    self.pos += 10
            self.op_cnt += 1
            return self.decode_operation(operation)
        except:
            raise InvalidInstructionException

    def decode_10x_args(self, op):
        return ''

    def decode_10t_args(self, op):
        a10t = self.args_10t.parse(op)
        offset = a10t['AA']
        args = ' {0: 05x} // {1:+05x}'.format((self.pos >> 1) - 1 + offset, offset)
        return args

    def decode_20t_args(self, op):
        a20t = self.args_20t.parse(op)
        offset = a20t['AAAA']
        args = ' {0: 05x} // {1:+05x}'.format((self.pos >> 1) - 2 + offset, offset)
        return args

    def decode_30t_args(self, op):
        a30t = self.args_30t.parse(op)
        offset = a30t['AAAAAAAA']
        args = ' {0: 09x} // {1:+09x}'.format((self.pos >> 1) - 3 + offset, offset)
        return args

    def decode_11x_args(self, op):
        a11x = self.args_11x.parse(op)
        args = ' v{0:d}'.format(a11x['AA'])
        return args

    def decode_11n_args(self, op):
        a11n = self.args_11n.parse(op)
        args = ' v{0:d}, #int {1:d} // #{1: 03x}'.format(a11n['A'],a11n['B'])
        return args

    def decode_12x_args(self, op):
        a12x = self.args_12x.parse(op)
        args = ' v{0:d}, v{1:d}'.format(a12x['A'],a12x['B'])
        return args

    def decode_21t_args(self, op):
        a21t = self.args_21t.parse(op)
        offset = a21t['BBBB']
        args = ' v{0:d}, {1: 05x} // {2:+05x}'.format(a21t['AA'],(self.pos >> 1) - 2 + offset, offset)
        return args

    def decode_21h_args(self, op):
        a21h = self.args_21h.parse(op)
        number = a21h['BBBB'] << 32
        args = ' v{0:d}, #{1:d} // #{1: 09x}'.format(a21h['AA'],number)
        return args

    def decode_w21h_args(self, op):
        a21h = self.args_21h.parse(op)
        number = a21h['BBBB'] << 64
        args = ' v{0:d}, #{1:d} // #{1: 17x}'.format(a21h['AA'],number)
        return args

    def decode_21s_args(self, op):
        a21s = self.args_21s.parse(op)
        args = ' v{0:d}, #int {1:d} // #{1: 05x}'.format(a21s['AA'],a21s['BBBB'])
        return args

    def decode_22t_args(self, op):
        a22t = self.args_22t.parse(op)
        offset = a22t['CCCC']
        args = ' v{0:d}, v{1:d}, {2: 05x} // {3:+05x}'.format(a22t['A'],a22t['B'],(self.pos >> 1) - 2 + offset, offset)
        return args

    def decode_f21c_args(self, op):
        a21c = self.args_21c.parse(op)
        #f = self.DexFile.get_field_by_id(a21c['BBBB'])
        f = {'type':'{type}','class':'{class}','name':'{field}'}
        args = ' v{0:d}, {1} [{2}].{3} // field@{4:04x}'.format(a21c['AA'],f['type'],f['class'],f['name'],a21c['BBBB'])
        return args

    def decode_t21c_args(self, op):
        a21c = self.args_21c.parse(op)
        #typen = self.DexFile.get_type_by_id(a21c['BBBB'])
        typen = '{type_name}'
        args = ' v{0:d}, [{1}] // type@{2:04x}'.format(a21c['AA'],typen,a21c['BBBB'])
        return args

    def decode_s21c_args(self, op):
        a21c = self.args_21c.parse(op)
        #st = self.DexFile.get_string_by_id(a21c['BBBB'])
        st = '{string}'
        args = ' v{0:d}, [{1}] // string@{2:04x}'.format(a21c['AA'],st,a21c['BBBB'])
        return args

    def decode_s31c_args(self, op):
        a31c = self.args_31c.parse(op)
        #st = self.DexFile.get_string_by_id(a31c['BBBBBBBB'])
        st = '{string}'
        args = ' v{0:d}, [{1}] // string@{2:08x}'.format(a31c['AA'],st,a31c['BBBBBBBB'])
        return args

    def decode_f22c_args(self, op):
        a22c = self.args_22c.parse(op)
        #f = self.DexFile.get_field_by_id(a22c['CCCC'])
        f = {'type':'{type}','class':'{class}','name':'{field}'}
        args = ' v{0:d}, v{1:d}, {2} [{3}].{4} // field@{5:04x}'.format(a22c['A'],a22c['B'],f['type'],f['class'],f['name'],a22c['CCCC'])
        return args

    def decode_t22c_args(self, op):
        a22c = self.args_22c.parse(op)
        #typen = self.DexFile.get_type_by_id(a22c['CCCC'])
        typen = '{type_name}'
        args = ' v{0:d}, v{1:d}, [{2}] // type@{3:04x}'.format(a22c['A'],a22c['B'],typen,a22c['CCCC'])
        return args

    def decode_22s_args(self, op):
        a22s = self.args_22s.parse(op)
        args = ' v{0:d}, v{1:d}, #int {2:d} // #{2: 05x}'.format(a22s['A'],a22s['B'],a22s['CCCC'])
        return args

    def decode_22b_args(self, op):
        a22b = self.args_22b.parse(op)
        args = ' v{0:d}, v{1:d}, #int {2:d} // #{2: 03x}'.format(a22b['AA'],a22b['BB'],a22b['CC'])
        return args

    def decode_22x_args(self, op):
        a22x = self.args_22x.parse(op)
        args = ' v{0:d}, v{1:d}'.format(a22x['AA'],a22x['BBBB'])
        return args

    def decode_23x_args(self, op):
        a23x = self.args_23x.parse(op)
        args = ' v{0:d}, v{1:d}, v{2:d}'.format(a23x['AA'],a23x['BB'],a23x['CC'])
        return args

    def decode_31t_args(self, op):
        a31t = self.args_31t.parse(op)
        offset = a31t['BBBBBBBB']
        args = ' v{0:d}, {1: 09x} // {2:+09x}'.format(a31t['AA'],(self.pos >> 1) - 3 + offset, offset)
        return args

    def decode_31i_args(self, op):
        a31i = self.args_31i.parse(op)
        #number = struct.unpack('<f',struct.pack('<l',a31i['BBBBBBBB']))
        args = ' v{0:d}, #{1:d} // {1: 09x}'.format(a31i['AA'],a31i['BBBBBBBB'])
        return args

    def decode_32x_args(self, op):
        a32x = self.args_32x.parse(op)
        args = ' v{0:d}, v{1:d}'.format(a32x['AAAA'],a32x['BBBB'])
        return args

    def decode_i35c_args(self, op):
        a35c = self.args_35c.parse(op)
        #m = self.DexFile.get_method_by_id(a35c['BBBB'])
        m = {'class':'{class}','name':'{method}'}
        method = ' // {0}->{1}'.format(m['class'],m['name'])
        args = ' '
        if (a35c['A'] == 0):
            args += '@{0:d}'.format(a35c['BBBB'])
        elif (a35c['A'] == 1):
            args += 'v{0:d} @{1:d}'.format(a35c['C'],a35c['BBBB'])
        elif (a35c['A'] == 2):
            args += 'v{0:d}, v{1:d} @{2:d}'.format(a35c['C'],a35c['D'],a35c['BBBB'])
        elif (a35c['A'] == 3):
            args += 'v{0:d}, v{1:d}, v{2:d} @{3:d}'.format(a35c['C'],a35c['D'],a35c['E'],a35c['BBBB'])
        elif (a35c['A'] == 4):
            args += 'v{0:d}, v{1:d}, v{2:d}, v{3:d} @{4:d}'.format(a35c['C'],a35c['D'],a35c['E'],a35c['F'],a35c['BBBB'])
        elif (a35c['A'] == 5):
            args += 'v{0:d}, v{1:d}, v{2:d}, v{3:d}, v{4:d} @{5:d}'.format(a35c['C'],a35c['D'],a35c['E'],a35c['F'],a35c['G'],a35c['BBBB'])
        return args + method

    def decode_t35c_args(self, op):
        a35c = self.args_35c.parse(op)
        #typen = self.DexFile.unfold_type_descriptor(self.DexFile.get_type_by_id(a35c['BBBB']))
        typen = '{type_name}'
        args = ' '
        if (a35c['A'] == 0):
            args += '[{0}] // type@{1:04x}'.format(typen,a35c['BBBB'])
        elif (a35c['A'] == 1):
            args += 'v{0:d}, [{1}] // type@{2:04x}'.format(a35c['C'],typen,a35c['BBBB'])
        elif (a35c['A'] == 2):
            args += 'v{0:d}, v{1:d}, [{2}] // type@{3:04x}'.format(a35c['C'],a35c['D'],typen,a35c['BBBB'])
        elif (a35c['A'] == 3):
            args += 'v{0:d}, v{1:d}, v{2:d}, [{3}] // type@{4:04x}'.format(a35c['C'],a35c['D'],a35c['E'],typen,a35c['BBBB'])
        elif (a35c['A'] == 4):
            args += 'v{0:d}, v{1:d}, v{2:d}, v{3:d}, [{4}] // type@{5:04x}'.format(a35c['C'],a35c['D'],a35c['E'],a35c['F'],typen,a35c['BBBB'])
        elif (a35c['A'] == 5):
            args += 'v{0:d}, v{1:d}, v{2:d}, v{3:d}, v{4:d}, [{5}] // type@{6:04x}'.format(a35c['C'],a35c['D'],a35c['E'],a35c['F'],a35c['G'],typen,a35c['BBBB'])
        return args

    def decode_i3rc_args(self,op):
        a3rc = self.args_3rc.parse(op)
        #m = self.DexFile.get_method_by_id(a3rc['BBBB'])
        m = {'class':'{class}','name':'{method}'}
        method = ' // {0}->{1}'.format(m['class'],m['name'])
        NNNN = a3rc['CCCC'] + a3rc['AA'] - 1
        args = ' v{0:d}..v{1:d} @{2:d}'.format(a3rc['CCCC'],NNNN,a3rc['BBBB'])
        return args + method

    def decode_t3rc_args(self,op):
        a3rc = self.args_3rc.parse(op)
        #typen = self.DexFile.unfold_type_descriptor(self.DexFile.get_type_by_id(a3rc['BBBB']))
        typen = '{type_name}'
        NNNN = a3rc['CCCC'] + a3rc['AA'] - 1
        args = ' v{0:d}..v{1:d},[{2}] // type@{3:04x}'.format(a3rc['CCCC'],NNNN,typen,a3rc['BBBB'])
        return args

    def decode_51l_args(self,op):
        a51l = self.args_51l.parse(op)
        #number = struct.unpack('<d',struct.pack('<q',a51l['BBBBBBBBBBBBBBBB']))
        args = ' v{0:d}, #{1:d} // #{1: 017x}'.format(a51l['AA'],a51l['BBBBBBBBBBBBBBBB'])
        return args

    def decode_operation(self, op):
        if type(op) == bytes:
            if op[0] in InstructionSet:
                method = getattr(self, 'decode_'+InstructionSet[op[0]][1]+'_args')
                if not method:
                    raise Exception("Method not implemented")
                args = method(op)
                return InstructionSet[op[0]][0] + args
            else:
                return '<unused>'
        elif type(op) == dict:
            return op

    def disassemble(self):
        self.pos = 0
        self.op_cnt = 0x0000
        while self.pos < len(self.RawBytes):
            instruction = []
            instruction.append(self.pos >> 1)
            instruction.append(self.extract_instruction())
            self.Listing.append(instruction)
        return self.Listing

def main():
    parser = OptionParser(usage = "usage: %prog [options] filename")
    (options, args) = parser.parse_args()

    if len(args) == 1:
        if not os.path.exists(args[0]):
            sys.exit('ERROR: File with bytecode %s wasn\'t found!' % args[0])
        else:
            f = open(args[0],mode='br')
            bytecode = f.read()
            if len(bytecode) > 0:
                d = DexDecompiler()
                d.load_bytearray(bytecode)
                pprint(d.disassemble())
    else:
        parser.print_help()

if __name__=="__main__": main()




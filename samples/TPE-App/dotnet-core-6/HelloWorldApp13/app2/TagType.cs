using System;
using System.Runtime.InteropServices;
public unsafe class TagType
{
    public enum TAG_RET
    {
        TAG_OK = 0,
        TAG_MALLOC_FAIL = -1,
        TAG_CREATE_THREAD_FAIL = -2,
        TAG_CREATE_FAIL = -3,
        TAG_GET_FAIL = -4,
        TAG_SET_FAIL = -5,
        TAG_SUB_FAIL = -6,
        TAG_PUB_FAIL = -7,
        TAG_PUB_MAP_FAIL = -8,
        TAG_PUB_ASSEMBLE_FAIL = -9,
        TAG_TRY_AGAIN = -10,
        TAG_FAIL = -99,
    }
    
    public enum TAG_VALUE_TYPE
    {
        TAG_VALUE_TYPE_BOOLEAN = 0,
        TAG_VALUE_TYPE_INT8,
        TAG_VALUE_TYPE_INT16,
        TAG_VALUE_TYPE_INT32,
        TAG_VALUE_TYPE_INT64,
        TAG_VALUE_TYPE_INT,          // deprecated
        TAG_VALUE_TYPE_UINT8,
        TAG_VALUE_TYPE_UINT16,
        TAG_VALUE_TYPE_UINT32,
        TAG_VALUE_TYPE_UINT64,
        TAG_VALUE_TYPE_UINT,         // deprecated
        TAG_VALUE_TYPE_FLOAT,
        TAG_VALUE_TYPE_DOUBLE,
        TAG_VALUE_TYPE_STRING,
        TAG_VALUE_TYPE_BYTEARRAY,
        TAG_VALUE_TYPE_RAW = 0xFF,
    }

    public struct TAG_OBJ
    {
        public UInt64          timestamp;
        public char            *tagName;
        public TAG_VALUE_TYPE  valType;
        public TAG_VALUE       tagValue;        
        public void            *user_data;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct TAG_VALUE
    {
        [FieldOffset(0)]
        public Boolean b;

        [FieldOffset(0)]
        public sbyte i8;

        [FieldOffset(0)]
        public Int16 i16;

        [FieldOffset(0)]
        public Int32 i32;

        [FieldOffset(0)]
        public Int64 i64;

        [FieldOffset(0)]
        public byte u8;

        [FieldOffset(0)]
        public UInt16 u16;
        [FieldOffset(0)]
        public UInt32 u32;
        [FieldOffset(0)]
        public UInt64 u64;
        [FieldOffset(0)]
        public float f;
        [FieldOffset(0)]
        public double d;
        [FieldOffset(0)]
        public TAG_VALUE_String str;
        [FieldOffset(0)]
        public TAG_VALUE_ByteArray ba;
        [FieldOffset(0)]
        public TAG_VALUE_RAW raw;
        
    }
    public struct TAG_VALUE_String
    {
        public char *ptr;
        public UInt16 length;
    }

    public struct TAG_VALUE_ByteArray
    {
        public byte *ptr;
        public UInt16 length;
    }
    public struct TAG_VALUE_RAW
    {
        public byte *ptr;
        public UInt16 length;
    }
}
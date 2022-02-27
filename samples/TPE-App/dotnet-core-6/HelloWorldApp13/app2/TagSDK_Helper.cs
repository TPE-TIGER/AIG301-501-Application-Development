using System.Runtime.InteropServices;

//********************************************
// Subscriber 
//********************************************
public class Subscriber : TagType
{   
    // Helper_Callback_Func be used between Helper and C Lib
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    public unsafe delegate void Helper_Callback_Func(IntPtr dx_tag_obj, UInt16 obj_cnt, IntPtr userData);

    // Caller_Callback_Func be used between Caller and Helper
    public delegate void Caller_Callback_Func(Dictionary<string,object> tag);

    // Load C Lib and declare 3 APIs
    private const string DLL_Path = "/usr/lib/arm-linux-gnueabihf/libmx-dx.so";
    [DllImport(DLL_Path)]
    private static extern UIntPtr dx_tag_client_init([In, MarshalAs(UnmanagedType.LPStr)] string moduleName, [MarshalAs(UnmanagedType.FunctionPtr)] Helper_Callback_Func callbackFn);

    [DllImport(DLL_Path)]
    private static extern TagType.TAG_RET dx_tag_sub(UIntPtr tagClient, [In, MarshalAs(UnmanagedType.LPStr)] string tagName, IntPtr userData);
    [DllImport(DLL_Path)]
    private static extern unsafe TagType.TAG_RET dx_tag_destroy(UIntPtr tagClient);
    
    // The handler link to C tag SDK Lib
    private UIntPtr _tagClient;

    // The callback function handlers
    public Caller_Callback_Func _callerFunc; 
    private Helper_Callback_Func _helperFunc;
     
    public Subscriber(Action<Dictionary<string,object>> callerFunction)
    {
        // Initial tag SDK by passing Helper's callback function
        _helperFunc = new Helper_Callback_Func(helperCallbackFunction);
        _tagClient = dx_tag_client_init("Subscriber", _helperFunc);

        // New callback function handler with Caller
        _callerFunc = new Caller_Callback_Func(callerFunction);
    }

    ~Subscriber()
    {
        // Release tag SDK memory
        dx_tag_destroy(_tagClient);
    }

    // Helper callback function extract tag object from C Lib, convert it to firendly C# dictionary, and pass tag to Caller's callback function
    public unsafe void helperCallbackFunction(IntPtr dx_tag_obj, UInt16 obj_cnt, IntPtr userData)
    {
        var returnTag = new Dictionary<string,object>();
        TAG_OBJ tagObj;
        tagObj = (TAG_OBJ)Marshal.PtrToStructure(dx_tag_obj, typeof(TAG_OBJ));
        
        var tagName = Marshal.PtrToStringAnsi((IntPtr)tagObj.tagName);
        var tagPatch = tagName.Split("/");
        returnTag.Add("prvdName",tagPatch[0]);
        returnTag.Add("srcName",tagPatch[1]);
        returnTag.Add("tagName",tagPatch[2]);
        returnTag.Add("timeStamp",tagObj.timestamp);
        var valueType = tagObj.valType;

        switch (valueType)
        {
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_BOOLEAN:
                returnTag.Add("dataType","boolean");
                returnTag.Add("dataValue",tagObj.tagValue.b);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT8:
                returnTag.Add("dataType","int8");
                returnTag.Add("dataValue",tagObj.tagValue.i8);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT16:
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT:
                returnTag.Add("dataType","int16");
                returnTag.Add("dataValue",tagObj.tagValue.i16);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT32:            
                returnTag.Add("dataType","int32");
                returnTag.Add("dataValue",tagObj.tagValue.i32);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT64:
                returnTag.Add("dataType","int64");
                returnTag.Add("dataValue",tagObj.tagValue.i64);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT8:
                returnTag.Add("dataType","uint8");
                returnTag.Add("dataValue",tagObj.tagValue.u8);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT16:
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT:
                returnTag.Add("dataType","uint16");
                returnTag.Add("dataValue",tagObj.tagValue.u16);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT32:            
                returnTag.Add("dataType","uint32");
                returnTag.Add("dataValue",tagObj.tagValue.u16);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT64:
                returnTag.Add("dataType","uint64");
                returnTag.Add("dataValue",tagObj.tagValue.u64);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_FLOAT:
                returnTag.Add("dataType","float");
                returnTag.Add("dataValue",tagObj.tagValue.f);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_DOUBLE:
                returnTag.Add("dataType","double");
                returnTag.Add("dataValue",tagObj.tagValue.d);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_STRING:
                returnTag.Add("dataType","string");
                returnTag.Add("dataValue", new string(Marshal.PtrToStringAnsi((IntPtr)tagObj.tagValue.str.ptr)));
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_BYTEARRAY:
                returnTag.Add("dataType","byte-array");
                byte[] managedArray1 = new byte[tagObj.tagValue.ba.length];
                Marshal.Copy((IntPtr)tagObj.tagValue.ba.ptr, managedArray1, 0, tagObj.tagValue.ba.length);
                returnTag.Add("dataValue", managedArray1);
                break;
            case TAG_VALUE_TYPE.TAG_VALUE_TYPE_RAW:
                returnTag.Add("dataType","raw");
                byte[] managedArray2 = new byte[tagObj.tagValue.raw.length];
                Marshal.Copy((IntPtr)tagObj.tagValue.raw.ptr, managedArray2, 0, tagObj.tagValue.raw.length);
                returnTag.Add("dataValue", managedArray2);
                break;
            default:
                Console.WriteLine("missing valueType: " +  valueType);
                return;
        }        
        _callerFunc(returnTag);
    } 
    public int subscribe(string prvdName, string srcName, string tagName)
    {
        if (_tagClient == null)
            return -1;

        IntPtr userData;
        userData = Marshal.StringToHGlobalUni(null);
        var SUBSCRIBE_TOPIC = prvdName + "/" + srcName + "/" + tagName;
        return (int) dx_tag_sub(_tagClient, SUBSCRIBE_TOPIC, userData);
    }
}


//********************************************
// Publisher
//********************************************
public unsafe class Publisher : TagType
{    
    // Load C Lib and declare 3 APIs
    const string DLL_Path = "/usr/lib/arm-linux-gnueabihf/libmx-dx.so";
    [DllImport(DLL_Path)]
    private static extern UIntPtr dx_tag_client_init([In, MarshalAs(UnmanagedType.LPStr)] string moduleName);
    [DllImport(DLL_Path)]
    private static extern unsafe TagType.TAG_RET dx_tag_pub(UIntPtr tagClient, [In, MarshalAs(UnmanagedType.LPStr)] string tagName, TAG_VALUE_TYPE tagValueType, TAG_VALUE tagVal, UInt64 timestamp);
    [DllImport(DLL_Path)]
    private static extern unsafe TagType.TAG_RET dx_tag_destroy(UIntPtr tagClient);
    
    // The handler link to C tag SDK Lib
    private UIntPtr _tagClient;
    // Initial tag SDK 
    public Publisher()
    {
        _tagClient = dx_tag_client_init("Publisher_app2");
    }
    // Release tag SDK Memory
    ~Publisher()
    {
        dx_tag_destroy(_tagClient);
    }

    // publish mehtod to build C Lib data structure
    public unsafe int publish(Dictionary<string,object> tag)
    {
        string prvdName, srcName, tagName, valueTypeString;
        TAG_VALUE_TYPE valueType;
        TAG_VALUE tagValue = new TAG_VALUE();
        try
        {            
            prvdName = (string)tag["prvdName"];
            srcName = (string)tag["srcName"];
            tagName = (string)tag["tagName"];
            valueTypeString = (string)tag["dataType"];      
            switch (valueTypeString.ToLower())
            {
                case "boolean":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_BOOLEAN;
                    tagValue.b = (bool)tag["dataValue"];
                    break;
                case "int8":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT8;
                    tagValue.i8 = (SByte)tag["dataValue"];
                    break;
                case "int16":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT16;
                    tagValue.i16 = (Int16)tag["dataValue"];
                    break;
                case "int32":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT32;
                    tagValue.i32 = (Int32)tag["dataValue"];
                    break;
                case "int64":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_INT64;
                    tagValue.i64 = (Int64)tag["dataValue"];
                    break;
                case "uint8":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT8;
                    tagValue.u8 = (Byte)tag["dataValue"];
                    break;
                case "uint16":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT16;
                    tagValue.u16 = (UInt16)tag["dataValue"];
                    break;
                case "uint32":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT32;
                    tagValue.u32 = (UInt32)tag["dataValue"];
                    break;
                case "uint64":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_UINT64;
                    tagValue.u64 = (UInt64)tag["dataValue"];
                    break;
                case "float":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_FLOAT;
                    tagValue.f = (float)tag["dataValue"];
                    break;
                case "double":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_DOUBLE;
                    tagValue.d = (Double)tag["dataValue"];
                    break;
                case "string":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_STRING;
                    tagValue.str.ptr = (char*)Marshal.StringToCoTaskMemAnsi((string)tag["dataValue"]);
                    break;
                case "byte-array":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_BYTEARRAY;
                    byte[] byteValue1 = (byte[])tag["dataValue"];
                    fixed (byte* a1 = byteValue1)
                    {
                        tagValue.ba.ptr = a1;
                        tagValue.ba.length = (ushort)byteValue1.Length;
                    }
                    break;
                case "raw":
                    valueType = TAG_VALUE_TYPE.TAG_VALUE_TYPE_RAW;
                    byte[] byteValue2 = (byte[])tag["dataValue"];
                    fixed (byte* a1 = byteValue2)
                    {
                        tagValue.raw.ptr = a1;
                        tagValue.raw.length = (ushort)byteValue2.Length;
                    }
                    break;
                default:
                    return -1;
            }
        } catch (Exception e) {
            Console.WriteLine(e.ToString());
            return -1;
        }
        return (int)publish(prvdName, srcName, tagName, valueType, tagValue);
    }    

    // publish method to invoke C Lib
    private TAG_RET publish(string prvdName, string srcName, string tagName, TAG_VALUE_TYPE valueType, TAG_VALUE tagValue)
    {
        if (_tagClient == null)
            return TAG_RET.TAG_PUB_FAIL;

        var PUBLISH_TOPIC = prvdName + "/" + srcName + "/" + tagName;
        return dx_tag_pub(_tagClient, PUBLISH_TOPIC, valueType, tagValue, (UInt64)0);
    }
}
// Referenced Assemblies
.assembly extern mscorlib
{
  .publickeytoken = (B7 7A 5C 56 19 34 E0 89 )
  .ver 4:0:0:0
}

.assembly testIF
{
  .hash algorithm 0x00008004
  .ver 0:0:0:0
}

.module testIF.exe

.class private auto ansi beforefieldinit Program
       extends [mscorlib]System.Object
{

  .method private hidebysig static void Main() cil managed
  {
    .entrypoint
    .maxstack 16
    .locals init (
[0] int32 a,
      [1] int32 c,
      [2] float32 s,
      [3] float32 d
    )
    ldloca a
    ldc.i4 6
    ldc.i4 2
    stind.i4
    ldloca c
    ldc.i4 200
    ldloc a
    mul
    stind.i4
    ldloca s
    ldc.r4 0.5
    ldc.r4 1.0
    div
    stind.r4
    ldloca d
    ldc.r4 10.0
    stind.r4
    ldloc a
	call void [mscorlib]System.Console::WriteLine(int32) 

    ldloc c
	call void [mscorlib]System.Console::WriteLine(int32) 

    ldloc s
	call void [mscorlib]System.Console::WriteLine(float32) 

    ldloc d
	call void [mscorlib]System.Console::WriteLine(float32) 

    ret
  } // end of method Program::Main

} // end of class Program

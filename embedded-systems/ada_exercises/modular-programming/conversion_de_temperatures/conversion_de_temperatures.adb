with Ada.Text_IO; use Ada.Text_IO;
with Ada.Float_Text_IO; use Ada.Float_Text_IO;

procedure conversion_de_temperatures is

   package Temp_Conv is 
      function To_Fahrenheit (C : Float) return Float;
      function To_Celsius (F : Float) return Float; 
   end Temp_Conv;

   package body Temp_Conv is 
      function To_Fahrenheit (C : Float) return Float is 
      begin
         return C * 9.0 / 5.0 + 32.0;
      end To_Fahrenheit;

      function To_Celsius (F : Float) return Float is 
      begin
         return ((F - 32.0) * 5.0 / 9.0);
      end To_Celsius;
   end Temp_Conv;

begin
   Put (Temp_Conv.To_Fahrenheit(100.0));
   New_Line;
   Put(Temp_Conv.To_Celsius(212.0));
   New_Line;
end conversion_de_temperatures;
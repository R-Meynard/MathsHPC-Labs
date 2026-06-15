with Ada.Text_IO; use Ada.Text_IO;

procedure compteur is
   package Counter is
      procedure Increment;
      procedure Reset;
      function Get return Integer;
   end Counter;

   package body Counter is 
      Value : Integer := 0;

      procedure Increment is
      begin
         Value := Value + 1; 
      end Increment;

      procedure Reset is
      begin 
         Value := 0; 
      end Reset;

      function Get return Integer is
      begin 
         return Value;
      end Get; 
   end Counter;
begin
   Counter.Increment;
   Counter.Increment;
   Counter.Increment;
   Counter.Reset;
   Counter.Increment;
   Put_Line (Integer'Image (Counter.Get));
end compteur;
-- main.adb 
with Ada.TEXT_IO; use Ada.TEXT_IO;
with Interfaces;
with Plot; use Plot;

procedure Main is

   P : Plot_Record := (
      Range_M => 15_000.0,
      Azimuth => 45.0,
      Elevation => 5.0,
      Velocity => -250.0,
      SNR => 12.5,
      Amplitude => 32768,
      Timestamp_Ms => 1_000
   );

begin
   Put_Line ("=== Plot dump ===");
   Put_Line ("Range_M    : " & Range_Meters'Image (P.Range_M));
   Put_Line ("Azimuth    : " & Azimuth_Deg'Image (P.Azimuth));
   Put_Line ("Elevation  : " & Elevation_Deg'Image (P.Elevation));
   Put_Line ("Velocity   : " & Velocity_Ms'Image (P.Velocity));
   Put_Line ("SNR        : " & SNR_dB'Image (P.SNR));
   Put_Line ("Amplitude  : " & Amplitude_Raw'Image (P.Amplitude));
   Put_Line ("Timestamp_Ms :" & Interfaces.Integer_64'Image (P.Timestamp_Ms));
end Main;
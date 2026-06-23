-- plot.ads

with Interfaces;

package Plot is
   type Azimuth_Deg is digits 6 range 0.0 .. 360.0;
   type Elevation_Deg is digits 6 range -90.0 .. 90.0;
   type Range_Meters is digits 6 range 0.0 .. 500_000.0;
   type Velocity_Ms is digits 6 range -3000.0 .. 3000.0;
   type SNR_dB is digits 6 range -20.0 .. 100.0;
   type Amplitude_Raw is mod 2**16;

   type Plot_Record is record 
      -- Localisation spherique (sortie CFAR / detection)
      Range_M : Range_Meters;
      Azimuth : Azimuth_Deg;
      Elevation : Elevation_Deg;

      -- Vitesse radiale (Doppler)
      Velocity : Velocity_Ms;

      -- Qualite de detection
      SNR : SNR_dB;
      Amplitude : Amplitude_Raw;

      -- Horodatage (en ms depuis epoch mission)
      Timestamp_Ms : Interfaces.Integer_64; 
   end record;
end Plot;
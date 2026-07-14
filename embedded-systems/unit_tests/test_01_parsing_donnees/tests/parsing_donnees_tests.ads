with AUnit; use AUnit;
with AUnit.Simple_Test_Cases; use AUnit.Simple_Test_Cases;

package Parsing_Donnees_Tests is

   type Test_Case is new AUnit.Simple_Test_Cases.Test_Case with null record;

   overriding function Name (T : Test_Case) return Message_String;
   overriding procedure Run_Test (T : in out Test_Case);

end Parsing_Donnees_Tests;
with AUnit.Run;
with AUnit.Reporter.Text;
with AUnit.Test_Suites; use AUnit.Test_Suites;
with Parsing_Donnees_Tests;

procedure Test_Runner is

   function Suite return Access_Test_Suite is
      Result : constant Access_Test_Suite := new Test_Suite;
   begin
      Result.Add_Test (new Parsing_Donnees_Tests.Test_Case);
      return Result;
   end Suite;

   procedure Run is new AUnit.Run.Test_Runner (Suite);
   Reporter : AUnit.Reporter.Text.Text_Reporter;

begin
   Run (Reporter);
end Test_Runner;
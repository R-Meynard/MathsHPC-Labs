with Ada.Text_IO;     use Ada.Text_IO;
with GNATCOLL.JSON;   use GNATCOLL.JSON;
with Parsing_Donnees; use Parsing_Donnees;

procedure Main is

   Log_File : File_Type;
   Items    : constant JSON_Array :=
     Lire_Donnees ("data/example-1-donnees.json");

   procedure Log (Message : String) is
   begin
      Put_Line (Log_File, Message);
      Put_Line (Message);
   end Log;

begin
   Create (Log_File, Out_File, "parsing.log");

   Log ("=== Début du parsing JSON ===");
   Log ("Fichier : data/example-1-donnees.json");
   Log ("Nombre d'entrées :" & Length (Items)'Image);
   Log ("");

   for I in 1 .. Length (Items) loop
      declare
         D : constant Entree_Sortie := Extraire_Entree (Get (Items, I));
      begin
         Log ("[entrée" & I'Image & "]");
         Log ("  id    = " & D.Id'Image);
         Log ("  a     = " & D.A'Image);
         Log ("  b     = " & D.B'Image);
         Log ("  somme = " & D.Somme'Image);
         Log ("  a + b ="
              & Integer'(D.A + D.B)'Image
              & "  attendu ="
              & D.Somme'Image
              & (if D.A + D.B = D.Somme then "  [OK]" else "  [ERREUR]"));
         Log ("");
      end;
   end loop;

   Log ("=== Fin du parsing JSON ===");
   Close (Log_File);

end Main;
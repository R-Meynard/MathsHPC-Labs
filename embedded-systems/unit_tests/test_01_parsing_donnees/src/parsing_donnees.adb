with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;
with Ada.Text_IO;           use Ada.Text_IO;

package body Parsing_Donnees is

   function Read_File (Path : String) return String is
      File   : File_Type;
      Buffer : Unbounded_String := Null_Unbounded_String;
      Line   : String (1 .. 4096);
      Last   : Natural;
   begin
      Open (File, In_File, Path);
      while not End_Of_File (File) loop
         Get_Line (File, Line, Last);
         Append (Buffer, Line (1 .. Last));
         Append (Buffer, ASCII.LF);
      end loop;
      Close (File);
      return To_String (Buffer);
   end Read_File;

   function Lire_Donnees (Path : String) return JSON_Array is
      JSON_Text : constant String     := Read_File (Path);
      Root      : constant JSON_Value := Read (JSON_Text, Path);
   begin
      return Root.Get ("donnees");
   end Lire_Donnees;

   function Extraire_Entree (Item : JSON_Value) return Entree_Sortie is
      Entree : constant JSON_Value := Item.Get ("entree");
      Sortie : constant JSON_Value := Item.Get ("sortie");
   begin
      return (Id    => Item.Get ("id"),
              A     => Entree.Get ("a"),
              B     => Entree.Get ("b"),
              Somme => Sortie.Get ("somme"));
   end Extraire_Entree;

end Parsing_Donnees;
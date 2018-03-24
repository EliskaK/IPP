<?php
 /*
  * IPP projekt 2018
  * 1. uloha
  * parse.php
  * Eliska Kadlecova, xkadle34
 */
  define('DEBUG', 0);
  define('STDERR', 'php://stderr');
  /*************************************************************************************/
  // INSTRUKCE:
      $instrukce = array("MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL",
                        "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT",
                        "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE",
                        "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP",
                        "JUMPIFEQ", "JUMPIFNEQ", "DPRINT", "BREAK");
  // INSTRUKCE ROZDĚLENY DO KATEGORIÍ:
      $instr_w_zero = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK");
      $instr_w_one_label = array("CALL", "LABEL", "JUMP");
      $instr_w_one_symb = array("PUSHS", "WRITE", "DPRINT");
      $instr_w_one_var = array("DEFVAR", "POPS");
      $instr_w_two_vs = array("MOVE", "INT2CHAR", "STRLEN", "TYPE", "NOT");
      $instr_w_two_vt = array("READ");
      $instr_w_three_vss = array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
                                 "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR");
      $instr_w_three_lss = array("JUMPIFEQ", "JUMPIFNEQ");
  /*************************************************************************************/
      // REGULÁRNÍ VÝRAZY:
      $comment = '/#.*$/';
      $boolregex = '/^(true|false|)$/i';
      $varregex = '/^(GF|LF|TF)@([[:alpha:]]|(_|-|\$|&|%|\*))([[:alnum:]]|(_|-|\$|&|%|\*))*/';
      $labelregex = '/^([[:alpha:]]|(_|-|\$|&|%|\*))([[:alnum:]]|(_|-|\$|&|%|\*))*/';
      $stringregex = '/^([[:alnum:]]|\\\\\d\d\d)*/';
      $intregex = '/^(((\+|\-)?\d+)|(\d*))$/';
      $typeregex = '/^(int|string|bool)/';
  /*************************************************************************************/
  // vypise chybove hlaseni a ukonci skript s danym navratovym kodem
  class calls {
    function call_error($errortext, $ret){
      fwrite(STDERR, $errortext);
      exit($ret);
    }
  }
  // kontrola inicializacniho retezce
  class is_ok_class {
    function is_init_line_ok($text) {
      $text = mb_strtolower($text, 'UTF-8');
      $init_text = mb_strtolower('.IPPcode18');
      if(strcmp($text, $init_text) === 0){
        return true;
      }
      else {
        return false;
      }
    }
  }

  // zjisteni typu
  function get_type($val){
    if(preg_match('/^(GF|TF|LF)@/', $val)){
      return "var";
    }
    elseif(preg_match('/^int@/', $val)){
      return "int";
    }
    elseif(preg_match('/^bool@/', $val)){
      return "bool";
    }
    elseif(preg_match('/^string@/', $val)){
      return "string";
    }
    elseif(preg_match('/^(string|int|bool|)$/i', $val)){
      return "type";
    }
    elseif (preg_match('/@/', $val)) {
      exit(calls::call_error("Error: Chybně zadaný typ konstanty.\n", 21));
    }
    else {
      return "label";
    }
  }
  // prepis nekterych znaku na XML zapis
  function special_chars($text){
    if(strpos($text, '&') !== false){
      $text = str_replace("&", "&amp;", $text);
    }
    if(strpos($text, '<') !== false){
      $text = str_replace("<", "&lt;", $text);
    }
    if(strpos($text, '>') !== false){
      $text = str_replace(">", "&gt;", $text);
    }
    return $text;
  }
  // overovani hodnoty u daneho typu
  function test_value($text, $type){
    global $varregex, $labelregex, $intregex, $stringregex, $boolregex, $typeregex;
    if($type == 'var'){
      if(preg_match($varregex, $text)) {
        return $text;
      }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu var.\n", 21));
    }
    elseif ($type == 'label') {
      if(preg_match($labelregex, $text)){
        return $text;
      }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu label.\n", 21));
    }
    elseif ($type == 'int') {
      if(preg_match($intregex, $text)){
        return $text;
      }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu int.\n", 21));
    }
    elseif ($type == 'string') {
      if(preg_match($stringregex, $text)){
        return $text;
      }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu string.\n", 21));
    }
    elseif ($type == 'bool') {
      if(preg_match($boolregex, $text)){
        return $text;
      }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu bool.\n", 21));
    }
    elseif ($type == 'type') {
      if(preg_match($typeregex, $text)){
          return $text;
        }
      else exit(calls::call_error("Error: Chybný tvar argumentu typu type.\n", 21));
    }
  }
/*******************************************************************************/
// ARGUMENTY:
    // pozice argumentu - implicitni hodnota
    $loc_pos = -1;
    $comm_pos = -1;
    $stats = false;
    $longopts = array(
      "stats:", // za musí být jeden parametr
      "loc",
      "comments",
      "help"
    );
    $my_args = getopt("", $longopts);
    if(count($argv) == 2){
      if(array_search("--help", $argv) !== false){
        echo "NÁPOVĚDA:\nTento skript čte zdrojový kód v IPPcode18 z stdin a vytváří z něj XML soubor,\nkterý tiskne na stdout.\n";
        echo "Volitelné parametry:\n";
        echo "--stats=file  -  určení výstupního souboru file (soubor musí existovat)\n";
        echo "--loc         -  použití pouze s --stats=file, vypíše do file počet instrukcí\n";
        echo "--comments    -  použití pouze s --stats=file, vypíše do file počet řádků s\nkomentářem\n";
        echo "--help        -  vypíše tuto nápovědu\n";
        exit(0);
      }
      else {
        return calls::call_error("Error: Samostatně lze použít pouze argument --help.\n", 10);
      }
    }
    if(count($argv) > 2 && count($argv) < 5){
      if(preg_grep('/--stats=.*/', $argv)){
        if(array_search("--loc", $argv) !== false){
          $temp = array_keys($my_args);
          $loc_pos = array_search("loc", $temp);
          if (DEBUG) echo $loc_pos . "\n";
        }
        if(array_search("--comments", $argv) !== false){
          $temp = array_keys($my_args);
          $comm_pos = array_search("comments", $temp);
          if (DEBUG) echo $comm_pos . "\n";
        }
        if(array_search("--help", $argv) !== false){
          return calls::call_error("Error: Špatně zadané argumenty. Použijte argument --help pro nápovědu.\n", 10);
        }
        $stats = true;
        $file = $my_args["stats"];
        $output = fopen($file, "w");
        if(!$output){
          return calls::call_error("Error: Soubor pro výstup statistik se nepodařilo otevřít.\n", 12);
        }
      }
      else{
        return calls::call_error("Error: Špatně zadané argumenty. Použijte argument --help pro nápovědu.\n", 10);
      }
    }
    if(count($argv) > 4){
      return calls::call_error("Error: Příliš mnoho argumentů.\n", 10);
    }
/*******************************************************************************/
    $file = fopen('php://stdin', "r");
    $num_line = 0;
    $order_num = 0;
    $num_comments = 0;
    if($file){
      while (($line = fgets($file)) !== false) {
        // line reading
        $line = trim($line);
        $line = preg_replace('/\s+/', ' ', $line); // odstraneni bilych znaku

        // komentare
        if (preg_match($comment, $line)) {
          $num_comments++;
          $position_comm = strpos($line, "#");
          $line = substr($line, 0, $position_comm); // smaze komentar
          //komentar byl na radku bez instrukce
        }
        // test na prvni řádek
        if(($num_line == 0) && (is_ok_class::is_init_line_ok($line) != true)) {
          return calls::call_error("Error: První řádek musí obsahovat: '.IPPcode18' - na velikosti nezáleží.\n", 21);
        }
        // inicializace XML
        elseif(($num_line == 0) && (is_ok_class::is_init_line_ok($line) == true)){
          $dom = new DomDocument("1.0", "UTF-8");
          $program = $dom->createElement('program');
          $program->setAttribute('language','IPPcode18');
          $num_line++;
        }
        elseif($line == "\n" || $line == '') {
          continue;
        }
        elseif ($num_line > 0){
          $order_num++;
          if(DEBUG) echo $line . "\n";
          $words = explode(' ', trim($line)); // ulozeni jednotlivych slov (instrukce + argumenty) do pole
          $words[0] = strtoupper($words[0]);
          if (array_search($words[0], $instrukce) !== false){
            $num_line++;
/************************************************************************************/
            // Instrukce bez argumentu:
            if(count($words) == 1 && array_search($words[0], $instr_w_zero) !== false){
              $instr = $dom->createElement('instruction');
              $instr->setAttribute('order',$order_num);
              $instr->setAttribute('opcode',$words[0]);
              $program->appendChild($instr);
            }
/************************************************************************************/
            // Instrukce s 1 argumentem:
            elseif (count($words) == 2) {
              if(array_search($words[0], $instr_w_one_var) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "var")));
                if(get_type($words[1]) == "var"){
                  $arg->setAttribute('type','var');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je var.\n", 21);
                }
                $instr->appendChild($arg);
              }
              elseif(array_search($words[0], $instr_w_one_symb) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                if(get_type($words[1]) == "var"){
                  $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[1]);
                  $arg = $dom->createElement('arg1', special_chars(test_value($value, get_type($words[1]))));
                }
                $arg->setAttribute('type', get_type($words[1]));
                $instr->appendChild($arg);
              }
              elseif(array_search($words[0], $instr_w_one_label) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "label"))) ;
                if(get_type($words[1]) == "label"){
                  $arg->setAttribute('type','label');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je label.\n", 21);
                }
                $instr->appendChild($arg);
              }
              else {
                if(DEBUG) echo $words[0] . "\n";
                return calls::call_error("Error: Instrukci chybí/přebývá argument.1\n", 21);
              }
            }
/************************************************************************************/
            // Instrukce s 2 argumenty:
            elseif (count($words) == 3){
              if(array_search($words[0], $instr_w_two_vs) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "var")));
                if(get_type($words[1]) == "var"){
                  $arg->setAttribute('type','var');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je var.\n", 21);
                }
                $instr->appendChild($arg);

                if(get_type($words[2]) == "var"){
                  $arg = $dom->createElement('arg2', special_chars(test_value($words[2], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[2]);
                  $arg = $dom->createElement('arg2', special_chars(test_value($value, get_type($words[2]))));
                }
                $arg->setAttribute('type', get_type($words[2]));
                $instr->appendChild($arg);
              }
              elseif(array_search($words[0], $instr_w_two_vt) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "var")));
                if(get_type($words[1]) == "var"){
                  $arg->setAttribute('type','var');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je var.\n", 21);
                }
                $instr->appendChild($arg);

                $arg = $dom->createElement('arg2', special_chars(test_value($words[2], "type")));
                if(get_type($words[2]) == "type"){
                  $arg->setAttribute('type','type');
                }
                else {
                  calls::call_error("Error: Očekávaný typ argumentu u instrukce je type.\n", 21);
                }
                $instr->appendChild($arg);
              }
              else {
                if(DEBUG) echo $words[0] . "\n";
                return calls::call_error("Error: Instrukci chybí/přebývá argument.2\n", 21);
              }
            }
/************************************************************************************/
            // Instrukce s 3 argumenty:
            elseif (count($words) == 4){
              if(array_search($words[0], $instr_w_three_vss) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value($words[1], "var")));
                if(get_type($words[1]) == "var"){
                  $arg->setAttribute('type','var');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je var.\n", 21);
                }
                $instr->appendChild($arg);

                if(get_type($words[2]) == "var"){
                  $arg = $dom->createElement('arg2', special_chars(test_value($words[2], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[2]);
                  $arg = $dom->createElement('arg2', special_chars(test_value($value, get_type($words[2]))));
                }
                $arg->setAttribute('type', get_type($words[2]));
                $instr->appendChild($arg);

                if(get_type($words[3]) == "var"){
                  $arg = $dom->createElement('arg3', special_chars(test_value($words[3], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[3]);
                  $arg = $dom->createElement('arg3', special_chars(test_value($value, get_type($words[3]))));
                }
                $arg->setAttribute('type', get_type($words[3]));
                $instr->appendChild($arg);
              }
              elseif(array_search($words[0], $instr_w_three_lss) !== false) {
                $instr = $dom->createElement('instruction');
                $instr->setAttribute('order',$order_num);
                $instr->setAttribute('opcode',$words[0]);
                $program->appendChild($instr);

                $arg = $dom->createElement('arg1', special_chars(test_value(preg_replace('/^.*?@/', '', $words[1]), "label")));
                if(get_type($words[1]) == "label"){
                  $arg->setAttribute('type','label');
                }
                else {
                  return calls::call_error("Error: Očekávaný typ argumentu u instrukce je label.\n", 21);
                }
                $instr->appendChild($arg);

                if(get_type($words[2]) == "var"){
                  $arg = $dom->createElement('arg2', special_chars(test_value($words[2], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[2]);
                  $arg = $dom->createElement('arg2', special_chars(test_value($value, get_type($words[2]))));
                }
                $arg->setAttribute('type', get_type($words[2]));
                $instr->appendChild($arg);

                if(get_type($words[3]) == "var"){
                  $arg = $dom->createElement('arg3', special_chars(test_value($words[3], "var")));
                }
                else {
                  $value = preg_replace('/^.*?@/', '', $words[3]);
                  $arg = $dom->createElement('arg3', special_chars(test_value($value, get_type($words[3]))));
                }
                $arg->setAttribute('type', get_type($words[3]));
                $instr->appendChild($arg);
              }
              else {
                if(DEBUG) echo $words[0] . "\n";
                return calls::call_error("Error: Instrukci chybí/přebývá argument.3\n", 21);
              }
            }
            else {
              return calls::call_error("Error: Špatný počet argumentů.\n", 21);
            }
          }
          else {
            return calls::call_error("Error: Instrukce byla zadána chybně.\n", 21);
          }

        } //if ($num_line > 0)

      } //while
      if(ftell($file) == false){
        calls::call_error("Error: Chybí zdrojový kód.\n", 21);
      }
      fclose($file); //uzavreny stdin
      // vypis XML
      $dom->appendChild($program);
      $dom->formatOutput = true;
      echo $dom->saveXML();
      // vypis statistik do souboru $output (--stats=file)
      if($stats){
        if($output){
          if ($comm_pos != -1 && $loc_pos != -1) {
            if ($loc_pos < $comm_pos) { // loc, comments
              $text = $order_num . "\n" . $num_comments . "\n";
              fwrite($output, $text);
            }
            else { // comments, loc
              $text = $num_comments . "\n" . $order_num . "\n";
              fwrite($output, $text);
            }
          }
          elseif ($comm_pos != -1) {
            fwrite($output, $num_comments . "\n");
          }
          elseif ($loc_pos != -1) {
            fwrite($output, $order_num . "\n");
          }
          fclose($output);
        }
      }
    }
    else {
      calls::call_error("Error: Nepodařilo se přistoupit na stdin.\n");
      return 11;
    }
?>

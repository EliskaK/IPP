<?php
$recurs = false;
$parse = "./parse.php";
$interpret = "./interpret.py";
$path = ".";

$longopts = array("help", "directory:", "recursive", "parse-script:", "int-script:");
$argumenty = getopt("", $longopts);
if (count($argumenty) != $argc-1) {
  fwrite(STDERR, "10: Neplatné argumenty. Zobrazte nápovědu pomocí parametru --help.\n");
  exit(10);
}
if ($argc != 1) {
  if (isset($argumenty["help"])) {
    if ($argc > 2) {
      fwrite(STDERR, "10: Neplatné argumenty. Zobrazte nápovědu pomocí parametru --help.\n");
      exit(10);
    }
    echo "NÁPOVĚDA test.php:\n";
    echo "Spuštění:\n./test.php [--help] [--directory=path] [--recursive] [--parse-script=file] [--int-script=file]\n";
    echo "--help              -- zobrazí tuto nápovědu\n";
    echo "--directory=path    -- v zadaném adresáři bude hledat testy (defaultně prochází\n";
    echo "                       aktuální adresář)\n";
    echo "--recursive         -- testy hledá rekurzivně i v podadresářích\n";
    echo "--parse-script=file -- soubor se skriptem parse.php (PHP 5.6) pro analýzu kódu\n";
    echo "                       v IPPcode18 (defaultně je zvolen parse.php v aktuálním\n";
    echo "                       adresáři)\n";
    echo "--int-script=file   -- soubor se skriptem interpret.py (PHP 5.6) pro\n";
    echo "                       reprezentaci kódu v IPPcode18 (defaultně je zvolen\n";
    echo "                       interpret.py v aktuálním adresáři)\n";
    exit(0);
  }
  if (isset($argumenty["directory"])) {
    $path = $argumenty["directory"];
  }
  if (isset($argumenty["recursive"])) {
    $recurs = true;
  }
  if (isset($argumenty["parse-script"])) {
    $parse = $argumenty["parse-script"];
  }
  if (isset($argumenty["int-script"])) {
    $interpret = $argumenty["int-script"];
  }

}
if($recurs){
  $iter = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path));
  foreach ($iter as $file) {
    if (is_dir($file) == true) {
      continue; // prohledavej dal dalsim zanorenim -- rekurzivni prohledavani
    }
    $files[] = $file->getPathname();
    $files = array_diff($files, [".",".."]);
  }
}
else {
  $dir = glob($path.'/*.*');
  foreach($dir as $file){
    $files[] = $file;
  }
}
//var_dump($files) . "\n";

// hledani .src souboru
foreach ($files as $src) {
  if(preg_match('/.+.src$/', $src)){
    $source_files [] = $src;
  }
}
if (empty($source_files)) {
  echo "11: Soubory pro testovani nebyly nalezeny.\n";
  exit(11);
}

for ($i=0; $i < count($source_files); $i++) {
  $test_names[$i] = preg_replace('/.src$/', "", $source_files[$i]);
}
//print_r($test_names) . "\n";

if(file_exists($parse) == false){
  echo "11: Skript parse.php nenalezen v daném adresáři.\n";
  exit(11);
}

$test_total = count($source_files);
$test_fail = 0;
$test_ok = 0;
$html = "";

foreach ($source_files as $test) {
  $test_name = str_replace(".src","", $test);
////////////////////////////////////////////////////////////////////////
  if (in_array($test_name . ".rc", $files)) {
    $ret_rc = file_get_contents($test_name . ".rc", $test);
  }
  else {
    $rc_file = fopen($test_name . ".rc", "w");
    if (!$rc_file){exit(11);}
    fwrite($rc_file, "0\n");
    $ret_rc = 0;
    fclose($rc_file);
  }

  if (in_array($test_name . ".in", $files)){
    $in_file = fopen($test_name . ".in", "c+");
    if (!$in_file){exit(11);}
  }
  else{
    $in_file = fopen($test_name . ".in", "c+");
    if (!$in_file){exit(11);}
  }

  if (in_array($test_name . ".out", $files)) {
    $out_file = fopen($test_name . ".out", "c+");
    if (!$out_file){exit(11);}
  }
  else{
    $out_file = fopen($test_name . ".out", "c+");
    if (!$out_file){exit(11);}
  }
  fclose($in_file);
  fclose($out_file);
///////////////////////////////////////////////////////////////////////
  $out = $test_name.".tmp";
  $input_inter = $test_name.".in";
  exec("php5.6 $parse < $test", $parse_out, $parse_ret);
  if($parse_ret != 0){ // skoncil s chybou; test, zda je chyba OK
    if ($ret_rc != $parse_ret) { // chybove kody nesedi
      $test_fail++;
      $html .= "<div><span class=\"dirr\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$parse_ret</strong></span></p></div>";
    }
    else { // chybove kody sedi
      $test_ok++;
      $html .= "<div><span class=\"dirg\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$parse_ret</strong></span></p></div>";
    }
  }
  else { // parser skoncil 0 -> pokracuj na interpret
    if(file_exists($interpret) == false){
      echo "11: Skript interpret.py nenalezen v daném adresáři.\n";
      exit(11);
    }
    $parse_out = implode("\n", $parse_out);
    $temp = tmpfile();
    fwrite($temp, $parse_out);
    exec("python3.6 ".$interpret." --source=".stream_get_meta_data($temp)['uri']. " < ".$input_inter." > " .$out, $int_out, $int_ret);
    fclose($temp);
    if ($int_ret != $ret_rc) { // intepret skoncil spatne - jinak nez se ocekavalo
      $test_fail++;
      $html .= "<div><span class=\"dirr\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$int_ret</strong></span></p></div>";
    }
    else { // navratovy kod se rovna s tim co bylo v souboru .rc
      if ($int_ret == 0) {  // pokud je navratovy kod 0 -> porovnej s .out
        $out_file = $test_name.".out";
        exec("diff $out $out_file", $diff, $rc_diff);
        if (count($diff) == 0){ // nelisi se, porovnani bylo uspesne
          $test_ok++;
          $html .= "<div><span class=\"dirg\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$int_ret</strong></span></p></div>";
        }
        else { // v diff neco je -> neproslo bez odlisnosti
          $test_fail++;
          $html .= "<div><span class=\"dirr\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$int_ret</strong></span></p></div>";
        }
      }
      else { // navratovy kod neni 0, ale chyba je ocekavana
        $test_ok++;
        $html .= "<div><span class=\"dirg\">$test</span><p>Očekávaný výstup:<strong> $ret_rc</strong></p><p>Reálný výstup: <span class=\"green\"><strong>$int_ret</strong></span></p></div>";
      }
    }
    unlink($out); // odstrani .tmp soubor
  }
}
//vypis html na stdout
  if(1){
    echo "<!DOCTYPE html>
    <html>
      <head>
         <title>IPPcode18</title>
         <meta charset=\"UTF-8\">
         <style type=\"text/css\">
         body {
         	overflow-x: hidden;
         	width: 980px;
         	margin: 0 auto;
         	background-color: grey;
         }
         .content {
         	background-color: rgba(255,255,255,0.6);
         	padding: 10px;
         	border-radius: 10px;
         	margin-top: 10px;
         }
         h1 {
         	text-align: center;
         	font-size: 54px;
         }
         .result {
         	text-align: center;
         	font-size: 24px;
         }
         .result span {margin-right: 25px;}
         .result span .green {
         	color: green;
         	margin-right: 5px;
         }
         .result span .red {
         	color: red;
         	margin-right: 5px;
         }
         .dirg, .dirr {
         	border: 2px solid green;
         	padding: 10px;
         	display: inline-block;
         }
         .dirr{
         	border: 2px solid red;
         }
         </style>
      </head>
      <body>
        <div class=\"content\">
         <h1>IPP2018</h1>
         <div class=\"result\">
         <span><span class=\"green\">&#10004;</span>: $test_ok</span>
         <span><span class=\"red\">&#x2716;</span>: $test_fail</span>
         <span>celkem: $test_total</span>
       </div>
       <hr>";
    echo "$html";
    echo "</div></body></html>";
  }
?>

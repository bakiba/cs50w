get-content .env | foreach {
    $name, $value = $_.split('=',2)
    set-content env:\$name $value
}
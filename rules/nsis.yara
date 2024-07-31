rule nsis_packer {
    strings:
        $nullsoft_string = "NullsoftInst"
    condition:
        all of them
}
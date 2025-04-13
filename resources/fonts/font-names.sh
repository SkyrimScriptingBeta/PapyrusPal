# For creating the QRC (note: you may need to clean up the output)

find . -type f -iname "*.ttf" | while read -r file; do
    font_name=$(fontforge -lang=ff -c 'Open($1); Print($fullname);' "$file" 2>/dev/null)
    echo "<file alias=\"fonts/$font_name.ttf\">$file</file>"
done

# For generating array in fonts.py

find . -type f -iname "*.ttf" | while read -r file; do
    font_name=$(fontforge -lang=ff -c 'Open($1); Print($fullname);' "$file" 2>/dev/null)
    echo "\"$font_name\","
done

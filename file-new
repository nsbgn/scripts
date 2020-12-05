#!/bin/bash
# Make a new file based on a template.
#
# Usage example:
#   file-new this-is-a-document.md some-image.svg

TEMPLATE_DIR="$(xdg-user-dir TEMPLATES)"

for F in "${@}"; do
    if [ -e "${F}" ]; then
        echo "File \"$F\" already exists." >&2 
        exit 1
    else
        # Progressively search: For a file called "a.jpg.tar.gz", we would
        # first look for a template ending in the full filename, then a
        # template for .jpg.tar.gz files, then tar.gz, etcetera. New *.gpg
        # files are the same as the corresponding base names, just encrypted.
        EXTENSION="$(basename --suffix .gpg -- "${F}")"
        while [ -n "${EXTENSION}" ]; do

            # File types for which we can generate a template (nonstandard so comes
            # first for graceful degradation)
            TEMPLATE="$(find -L "$TEMPLATE_DIR/exec" \
                -maxdepth 1 -type f -iname '*'"$EXTENSION" -print -quit | grep .)"
            if [ "$?" -eq 0 ]; then
                if [[ "$F" == *".gpg" ]] ; then
                    "$TEMPLATE" "$F" | gpg --encrypt > "$F"
                else
                    "$TEMPLATE" "$F" > "$F"
                fi
                exit 0
            fi

            # File types for which there is a template
            TEMPLATE="$(find -L "$TEMPLATE_DIR" \
                -maxdepth 1 -type f -iname '*'"$EXTENSION" -print -quit | grep .)"
            if [ "$?" -eq 0 ]; then
                if [[ "$F" == *".gpg" ]] ; then
                    gpg -o "$F" --encrypt < "$TEMPLATE"
                else
                    cp "$TEMPLATE" "$F"
                fi
                exit 0
            fi

            if [[ "${EXTENSION}" == *.* ]]; then
                EXTENSION="${EXTENSION#*.}"
            else
                EXTENSION=""
            fi
        done
        
        # Otherwise, just make an empty file
        touch "${F}"
    fi
done


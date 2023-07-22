#!/bin/bash
O=${O:=1}  # output in oneline
F=${F:=}  # specify file other than generate a file fom script

function joinlines() {
    # join line which starts with ' '
    if [ "$O" = 1 ];then
        sed -e '/^\s*$/d' -e 's/\<no value\>/<no-value>/g' | \
        awk 'NF>0{if (/^[[:space:]]/) { printf "%s", $0; next } else { printf "\n%s", $0 }} END { printf "\n" }'
    else
        cat
    fi
}

function remove_empty_lines() {
    sed -e '/^\s*$/d'
}

function print_go_template_file_example() {
cat <<'EOF'
{{/* Gobal variables here */}}
{{/* key of annnotations or labels */}}
{{- $instanceid := "vci.vke.volcengine.com/instance-id" -}}
{{- $labels_app := "app" -}}
{{- $conditionType := "Ready" -}}
{{- range .items -}}
    {{- $found := "" -}}{{- range $obj := .status.conditions -}}{{- if eq $obj.type $conditionType -}}{{- $found = $obj.lastTransitionTime -}}{{- end -}}{{- end -}}

    {{/* Frist line printed here, and should be no whitespace at begining */}}
    {{- .metadata.namespace }} {{ .metadata.name }}
    {{ .status.phase }}
    {{/* example for kv block */}}
    {{ if .metadata.annotations }} {{- index .metadata.annotations $instanceid -}} {{- end }}

    {{ if .metadata.labels }} {{- index .metadata.labels $labels_app -}} {{- end }}

    {{ range .spec.containers -}}
        {{ .name }}:{{ .image }}
    {{- end }}
    {{ $found }}
{{ end -}}
EOF
}

function print_go_template_file() {
cat <<'EOF'
{{/* Gobal variables here */}}
{{/* key of annnotations or labels */}}
{{- $instanceid := "vci.vke.volcengine.com/instance-id" -}}
{{- $labels_app := "app" -}}
{{- $conditionType := "Ready" -}}
{{- range .items -}}
    {{- $found := "" -}}{{- range $obj := .status.conditions -}}{{- if eq $obj.type $conditionType -}}{{- $found = $obj.lastTransitionTime -}}{{- end -}}{{- end -}}

    {{/* Frist line printed here, and should be no whitespace at begining */}}
    {{- .metadata.namespace }} {{ .metadata.name }}
    {{ .status.phase }}
    {{/* example for kv block */}}
    {{ if .metadata.annotations }} {{- index .metadata.annotations $instanceid -}} {{- end }}

    {{ if .metadata.labels }} {{- index .metadata.labels $labels_app -}} {{- end }}

    {{ range .spec.containers -}}
        {{ .name }}:{{ .image }}
    {{- end }}
    {{ $found }}
{{ end -}}
EOF
}


tmpf=/tmp/pod-go-pattern
if test -f "$F";then
    tmpf=$F
else
    print_go_template_file | remove_empty_lines > $tmpf
fi

kubectl get --all-namespaces pods -o go-template-file=$tmpf | joinlines

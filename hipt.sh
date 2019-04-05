#!/bin/bash

RULE_MATCH_="-p tcp --dport 32145"
RULE_MATCH_="-p tcp"
RULE_MATCH_="-s 192.168.10.137 -p tcp"
RULE_MATCH_="-d 172.16.70.51 -p icmp"

#HIPT_RULE_MATCH=${RULE_MATCH_}
RULE_JUMP="-j LOG --log-level 6 --log-prefix hipt-%t-%c-%l"

COMMENT=${COMMENT:-hipt-label}


del_all() {
    local t x c l
    local res
    local ts="$@"
    if test -z "$ts";then
        ts="raw mangle nat filter"
    fi

    for t in $ts
    do
        while res=$(iptables -L -n --line-number -t $t|grep "^Chain \|$COMMENT"  |grep -m1 -B1 "$COMMENT")
        do
            { read x c x; read l x; } <<<"$res" ;
            echo "$t.$c: $c $x"
            iptables -t $t -D $c $l
        done
    done
}

_insert_for_table_chain() {
    local t="$1"
    local cs="$2"
    local l="${3:-1}"
    local c rj
    shift
    shift
    if test -z "$HIPT_RULE_MATCH";then
        echo "Error: env HIPT_RULE_MATCH is not set. exit"
        exit 1
    fi
    for c in $cs
    do
        rj=${RULE_JUMP//%t/$t}
        rj=${rj//%c/$c}
        rj=${rj//%l/$l}
        echo "iptables -t $t -I $c $l -m comment --comment \"$COMMENT:$t:$c:\" $HIPT_RULE_MATCH $rj"
        iptables -t $t -I $c $l -m comment --comment "$COMMENT:$t:$c:" $HIPT_RULE_MATCH $rj
    done
}

insert_for_all_tables() {
    _insert_for_table_chain mangle "PREROUTING OUTPUT INPUT POSTROUTING FORWARD"
    _insert_for_table_chain raw "PREROUTING OUTPUT"
    _insert_for_table_chain nat "PREROUTING OUTPUT INPUT POSTROUTING"
    _insert_for_table_chain filter "OUTPUT INPUT FORWARD"
}

insert_for_one_table() {
    local t="$1"
    local cs="$(iptables -L -n -t $t |awk '{ if ($1 == "Chain") {print $2}}')"
    _insert_for_table_chain "$t" "$cs"
}

insert_for_one_chain() {
    local t="$1"
    local c="$2"
    local n=$(iptables -t $t -L $c -n | grep -v '^Chain'|wc -l)

    local i
    for i in $(seq $n)
    do
        _insert_for_table_chain $t $c $((i*2-1))
    done
}

PRINT_NUM=
ZERO=
_statistics_simply() {
    local line11=
    local line12=
    local line13=
    local t="$1"
    local c=
    while read line11 line12 line13 line14
    do
        if test -z "$line11";then
            break
        fi
        if [ "$line11" = "Chain" ];then
            c=${line12%ROUTING}
            continue
        else
            if [[ "$line14" =~ "$COMMENT" ]];then
                if [ "$PRINT_NUM" = "1" -a "$line12" = "0" ];then
                    continue
                fi
                if test -n "$t";then
                    printf "===== %-7s ===== \n" "$t:"
                    t=
                fi
                printf "%16s %3s %10s %10s %s\n" "$c" "$line11" "$line12" "$line13" "$line14"
            fi
        fi
    done
}

statistics_show() {
    while test -n "$1"
    do
        [ "X$1" = "X-n" ] && PRINT_NUM=1
        [ "X$1" = "X-Z" ] && ZERO=1
        shift
    done

    if [ "$ZERO" = 1 ];then
        for t in raw mangle nat filter
        do
            iptables -t $t -Z
        done
    fi

    for t in raw mangle nat filter
    do
        iptables -L --line -n -v -t $t |grep -v '^\s*$'  | _statistics_simply $t "$@"
    done  | sed 's/LOG.*\/\*/\/*/'
}

op="$1"
shift
case "$op" in
    del)
        del_all "$@";;
    ia)
        insert_for_all_tables;;
    it)
        insert_for_one_table $1;;
    ic)
        insert_for_one_chain $1 $2;;
    stat)
        statistics_show "$@";;
    *)
        cat <<EOF
        $0 del|ia|it|ic|stat
            ia                  insert for all tables
            it [table]          insert for one table
            ic [table] [chain]  insert for one table chain
            del  [table] ..     delete from tables
            stat [table] ..     show statistics of tables
EOF
        ;;
esac


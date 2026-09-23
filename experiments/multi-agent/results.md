# Results

两个脚本都跑了 `trap` 和 `clear`，每次 mock call 固定记作 `120 ms`。

```text
scenario  single answer                    multi-agent answer             calls  estimated model latency
trap      yes; 24.0 ms                     no; verified estimate 25.0 ms  1 / 3  120 / 360 ms
clear     yes; 14.5 ms                     yes; verified estimate 15.0 ms 1 / 3  120 / 360 ms
```

`trap` 里，单 Agent 把 miss 的 latency 算成了 backend cost，漏了前面的 lookup。analyst 也算出 24.0 ms。checker 补上那 5 ms lookup 后得到 25.0 ms，答案从 yes 变成 no。

`clear` 里也发生了修正，14.5 ms 变成 15.0 ms。两边都低于 threshold，答案还是 yes。三次调用在这里没有换来更好的最终结果。

## Notes

`trap` 里的两次额外调用确实改对了答案，`clear` 没有。checker 有用，是因为它重新算了 miss path。只换一个 role 名字不会发生这种事。

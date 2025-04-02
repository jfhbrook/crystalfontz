# DBus Client CLI

Assuming `crystalfontzd` is running, you may interact with the service using `crystalfontzctl`:

```sh
$ crystalfontzctl --help
TODO
```

The interface is similar to the vanilla `crystalfontz` CLI. However, there are a few differences:

1. By default, `crystalfontzctl` will connect to the `system` bus. To connect to the local bus, set the `--user` flag.
2. Configuration commands do not reload `crystalfontzctl`'s configuration. Instead, they will update the relevant config file, and show the differences between the file config and the service's loaded config.
3. If the config file isn't owned by the user, `crystalfontzctl` will attempt to run editing commands with `sudo`.

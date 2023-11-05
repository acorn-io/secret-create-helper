## Cred helper

### What is this?

Acorn's sometimes provision 3rd party services, and users will need to provide some form of credentials to access these services. This Acorn provides a webpage to explain to users where to get these credentials and provides an input form to create the Acorn secret.

### How do I use this?

This Acorn is meant to be used as a nested Acorn. It can be used to create a secret on it's own, but it's utility is when you use it with other Acorns.

To add to your Acornfile, define the acorn in the `acorns` section of the Acornfile. You will need to provide a comma separated list of keys that you want the user to provide.

Here is an example of how to add this Acorn to your Acornfile:

```cue
acorns: helper: {
    image: "ghcr.io/acorn-io/secret-create-helper:v#.#.#"
    serviceArgs: {
        secretKeys: "public_key,private_key,project_id"
        instructions: localData.credInfo
    }
}

// ...

localData: credInfo: """
    ## Instructions provided by the author
    ## Get your credentials from [here](https://example.com/apikeys)
    """
```

When run, the helper acorn will create an opaque secret with the keys provided and the user information. The way to handle this is to use `alias` on the secret you want to have bound in.

```cue
// ...
secrets: "api-keys": alias: "helper.output"
// ...
```

### What does this look like?

When this has been added to the Acornfile, when launched the user will see an endpoint to open the page to prompt the user. The user clicks on the link and is taken to the page that provides instructions and a form to create the secret needed to provision the service.

### Examples

[Mongodb Atlas](https://github.com/acorn-io/mongodb-atlas)

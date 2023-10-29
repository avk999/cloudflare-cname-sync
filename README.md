# Cloudflare cnames generator
## Motivation
Cloudflare Argotunnels (aka Zero-Trust) provide a very convenient (and free!!) way to expose an on-prem service to the outside world. 
To expose a service one needs to:
1. Host a DNS zone which will contain the exposed service on Cloudflare
2. Configure and run a tunnel
   * tunnel can be referenced as a `uuid.cfargotunnel.com`. While this hostname doesn't actually exist traffic to any CNAME referenced will be sent down the tunnel.
   * tunnel endpoint should be pointing to the service which serves your cluster ingress controller (probably a load-balancer service named like `ingress-nginx-controller`)
3. create a CNAME in the DNS zone on Cloudflare

The great description of the moving parts is available at [Letscloud](https://letsdocloud.com/2021/06/expose-kubernetes-service-using-cloudflare-argo-tunnel/).

## What is here
Here is a controller which helps to create those CNAMES (step 3 above). It is based on [Metacontroller](https://metacontroller.github.io/), I use version 4.11.5.
Metacontroller is a "controller controller" - it lets you to reduce the whole controller machinery to a webhook. Read the docs.
The generated service should be picked up by [External-dns](https://github.com/kubernetes-sigs/external-dns) controller. As of now `ExternalName`-type service is the only way to make External-dns to create a CNAME record. If you know of any other way please let me know.

## Prerequisites
1. A kubernetes cluster 
2. Running Ingress controller (I use nginx-ingress but it shouldn't matter)
3. External-dns running and configured for Cloudflare
4. Cloudflared installed and running, as described in [Letscloud](https://letsdocloud.com/2021/06/expose-kubernetes-service-using-cloudflare-argo-tunnel/).
5. Metacontroller installed and running. This cnames generator doesn't require any specific metacontroller configuration so ` helm install -n metacontroller --create-namespace metacontroller oci://ghcr.io/metacontroller/metacontroller-helm --version=v4.11.5` should be sufficient.
6. Clear understanding that you are going to expose a service running on your hardware to the big bad outside world.

## Configuration
go through `values.yaml` You must set `tunnel_id` to the id of your tunnel. Everything else may be left as is. `labelSelector` is a safety measure - if it is set only ingresses with `cf-external: "true"` label will be allowed. `prefix` string is used to prefix the name of generated services.

Run `helm install -f values.yaml -n some-namespace cf-cname-hook charts/`, add a label to one of your ingresses and in a few minutes your service is available from outside.

Pull requests etc are very welcome.

Thanks to `gubi` for Letscloud doc, cool guys who did `Metacontroller`, [Cloudflare](https://cloudflare.com) for the fantastic and free services and of course K8S authors for External-dns and k8s itself!

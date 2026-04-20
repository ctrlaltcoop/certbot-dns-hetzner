# Changelog

## 4.0.0

* use hcloud instead of dns-lexicon (only support Hetzner Cloud API)

## 3.0.0

* use `dns-lexicon-coop` while MR for `dns-lexicon` is open
* support the new Hetzner Cloud API

## 2.0.1

* consider private domains in tldextract
* use lexicon.client.Client instead of deprecated lexicon.providers.hetzner
* add default_propagation_seconds to parse_arguments

## 2.0.0

* support certbot >= 2.0
* use `dns-lexicon` instead of custom code

## 1.0.3

* fix faulty publish script in github actions

## 1.0.2

* fixes bug #2

## 1.0.1

* package available on pypi

## 1.0.0

* Initial release
* Working certbot plugin to authenticate via dns-01 challenge on dns.hetzner.com

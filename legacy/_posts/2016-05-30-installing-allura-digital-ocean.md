---
layout: post
title: Installing Apache Allura on Digital Ocean 
tags:
- gsoc
---

Installing Apache Allura on your [Digital Ocean](http://digitalocean.com) droplet is now as easy as typing `make install`.

[Apache Allura](http://allura.apache.org) is a Software Forge that powers [SourceForge.net](http://sourceforge.net). Today,
I created a Makefile that simplifies the process of setting up Allura on a Digital Ocean droplet. The source code is hosted
on [https://forge-allura.apache.org/u/rhnvrm/allura-install/ci/master/tree/](https://forge-allura.apache.org/u/rhnvrm/allura-install/ci/master/tree/)
and on [github](http://github.com/rhnvrm/allura-install).

Here are the steps to get started with deploying your own instance of Apache Allura.

1. Set up your [digital ocean](http://digitalocean.com) account and spin up a new `Ubuntu 14.04` droplet.
2. SSH into your droplet's root `ssh root@<DO_id>` and
clone the repository using `git clone https://rhnvrm@forge-allura.apache.org/git/u/rhnvrm/allura-install`
3. Change your working directory into the cloned repository. `cd allura-install`
4. Install `git` and `make` using `apt-get install git make`
5. Run `make install`

If you face an error during a make step, report it to the issue tracker on [github](http://github.com/rhnvrm/allura-install/issues).

If it is an error that you can fix or due to some network errors, you can run the next step listed in the make file.

Suppose, you faced an error during the `npm install` inside the `initialize-allura-taskd`, you can run `make initialize-allura-taskd` again and
then run each next step in a simlar fashion (such as `initialize-allura-data`)

Finally, run `make start` (only required if `make` failed during a certain step)



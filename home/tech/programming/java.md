---
title: "Java"
tags:
  - java
  - programming
---

# :material-language-java:{ .anim-fade } Java

Most of these notes are from the book *Java Projects* by *Peter Verhas*.

## Maven build lifecycle targets

- `validate` - validate the project is correct and all necessary information is available
- `compile` - compile the source code of the project
- `test` - test the compiled source code using a suitable unit testing framework. These tests should not require the code be packaged or deployed
- `package` - take the compiled code and package it in its distributable format, such as a JAR.
- `verify` - run any checks on results of integration tests to ensure quality criteria are met
- `install` - install the package into the local repository, for use as a dependency in other projects locally
- `deploy` - done in the build environment, copies the final package to the remote repository for sharing with other developers and projects.

From [the official documentation](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html).

## JConsole over SSH with SOCKS Proxy

This is from [here](http://stackoverflow.com/questions/15093376/jconsole-over-ssh-local-port-forwarding): 
Create the SSH socks proxy locally on some free port (e.g. 7777):

```
ssh -fN -D 7777 user@firewalled-host
```

Run JConsole by specifying the SOCKS proxy (e.g. localhost:7777) and
the address for the JMX server (e.g. localhost:2147)

```
jconsole -J-DsocksProxyHost=localhost -J-DsocksProxyPort=7777 service:jmx:rmi:///jndi/rmi://localhost:2147/jmxrmi -J-DsocksNonProxyHosts=
```

## JShell

- `/list -start` - shows modules imported at startup.
- `/edit <number>` - edit that line in a new window.
- `/set editor "vi"` - use vi instead of the default graphical edit pad.
- `/save abc.java` - save current buffer to file.
- `/load abc.java` - load from file into shell.
- `/-1` - execute last snippet.
- `/1` - execute first snippet.
- `/drop N` - drop Nth snippet.
- `/vars` - show only variables that were defined in snippets.
- `/types` - show only classes that were defined in snippets.

## Javap

- `javap TestDecompile.class` - decompile .class file to human
  readable format. Does not show content of methods though.

- `javap -c TestDecompile.class` - show jvm bytecode in human readable
  -form, including methods.

## Jar files

These are zip files that have a `META-INF` folder with a `Manifest.mf`
file inside.

To create a jar file:

``` sh
jar -cf hello.jar HelloWorld.class
```

And to run:

``` sh
java -cp hello.jar HelloWorld
```

To see contents of a jar:

``` sh
jar -tf hello.jar
```

## Runtime/debugging

- `jps` - Shows all runnning java processes.

- `jvisualvm` - If you have it, it shows the java processes on the
  system with details on threads, profiler etc.

- `-Xagentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=7896`
  Use these args to start a process in debugging mode.
    - `agentlib=jdwp` - Load the `jdwp` agent, for debugging.

    - `transport=dt_socket` - for connecting a debugging client over
      the network.
    
    - `server=y` - this one is the server half of the debugging.

    - `suspend=y` - don't start executing until a client debugger
      attaches.

    - `address=7896` - port we listen on.

## Maven

- Expected directory structure: Java files are in `src/main/java` as
  well as `src/test/java`. Resource files are under
  `src/main/resources` and `src/test/resources`.

- `mvn archetype:generate`: Generates a skeleton of a project based on
  your inputs (package name, versioning, project name, etc).

- Edit `pom.xml` and set the jdk version there.. the default may be
  old. Java 9 onwaards doesn't generate the `.class` format. You
  should have this added to the default .xml file:

```xml
<build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.8.0</version>
        <configuration>
            <source>1.11</source>
            <target>1.11</target>
            <release>11</release>
        </configuration>
      </plugin>
    </plugins>
  </build>
```

- `mvn package` - compile, test, bundle.

## Interfaces

- All fields (i.e. class variables) default to `static final`. All
  methods default to `public`.

## Field types

- `static` - One instance per class, not per  object.

- `final` - Initialized exactly once, either where declared or
- somewhere in the constructor. Immutable after that.

- `transient` - Do not serialize/deserialize this field.

- `volatile` - Treat as a field that may be accessed by multiple
  threads. If not volatile, the value may be stored in a processor
  cache or registry for faster access.

## Things to find out later

- See how to create a call graph in eclipse.

- `final` keyword?

    - *Answer*: when used with a variable, it (a) blocks reassignment,
      and (b) limits existence to that block. e.g. a `final String tmp = orig`
      inside a for loop cannot be reassigned with a different
      value. The value does not exist outside the block it is defined
      in. Good practice to declare this often as it means a variable
      is guaranteed not to change in value.



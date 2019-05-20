%define beta b6

Name:           bsh
Version:        2.0
Release:        1
Summary:        Lightweight Scripting for Java
Group:		System/Libraries
License:        (SPL or LGPLv2+) and Public Domain
Source0:        https://github.com/beanshell/beanshell/archive/%{version}%{beta}/%{name}-%{version}%{beta}.tar.gz
Source1:        http://central.maven.org/maven2/org/apache-extras/beanshell/bsh/%{version}%{beta}/bsh-%{version}%{beta}.pom
Source3:        %{name}-desktop.desktop

Patch0:		bsh-2.0b6-openjdk12.patch

BuildRequires:  jdk-current
BuildRequires:  ant imagemagick desktop-file-utils
BuildRequires:  jmod(javax.servlet)
BuildRequires:	javapackages-local
URL:            http://www.beanshell.org/
BuildArch:      noarch

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java.  BeanShell
executes standard Java statements and expressions, in addition to
obvious scripting commands and syntax.  BeanShell supports scripted
objects as simple method closures like those in Perl and
JavaScript(tm).  You can use BeanShell interactively for Java
experimentation and debugging or as a simple scripting engine for your
applications.  In short: BeanShell is a dynamically interpreted Java,
plus some useful stuff.  Another way to describe it is to say that in
many ways BeanShell is to Java as Tcl/Tk is to C: BeanShell is
embeddable - You can call BeanShell from your Java applications to
execute Java code dynamically at run-time or to provide scripting
extensibility for your applications.  Alternatively, you can call your
Java applications and objects from BeanShell; working with Java
objects and APIs dynamically.  Since BeanShell is written in Java and
runs in the same space as your application, you can freely pass
references to "real live" objects into scripts and return them as
results.

%prep
%autosetup -p1 -n beanshell-%{version}%{beta}
# No prebuilt jars...
rm -rf lib
# Get rid of HTML4 constructs in javadoc
find . -name "*.java" |xargs sed -i -e 's,<tt>,<code>,g;s,</tt>,</code>,g'

%build
. %{_sysconfdir}/profile.d/90java.sh

TOPDIR="`pwd`"

buildjar() {
	if ! [ -e module-info.java ]; then
		MODULE="$1"
		shift
		echo "module $MODULE {" >module-info.java
		find . -name "*.java" |xargs grep ^package |cut -d: -f2 |sed -e 's,^.*package[[:space:]]*,,;s,\;.*,,' -e 's/^[[:space:]]*//g' -e 's/[[:space:]]*\$//g' |sort |uniq |while read e; do
			echo "	exports $e;" >>module-info.java
		done
		for i in "$@"; do
			echo "	requires $i;" >>module-info.java
		done
		echo '}' >>module-info.java
	fi
	find . -name "*.java" |xargs javac -p %{_javadir}/modules:${TOPDIR}/lib
	find . '!' -name "*.java" |xargs jar cf $MODULE-%{version}.jar
	jar i $MODULE-%{version}.jar
}
cd asm/src
buildjar bsh.org.objectweb.asm
cd ../..
mkdir lib
mv asm/src/*.jar lib
cd src
buildjar bsh bsh.org.objectweb.asm java.desktop javax.servlet
mv bsh-%{version}.jar ../lib

%install
mkdir -p %{buildroot}%{_javadir}/modules %{buildroot}%{_mavenpomdir}
cp lib/*.jar %{buildroot}%{_javadir}/modules
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh.jar
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh-classpath.jar
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh-commands.jar
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh-core.jar
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh-reflect.jar
ln -s modules/bsh-%{version}.jar %{buildroot}%{_javadir}/bsh-util.jar
cp %{S:1} %{buildroot}%{_mavenpomdir}/
%add_maven_depmap bsh-%{version}%{beta}.pom bsh-%{version}.jar

%files -f .mfiles
%{_javadir}/modules/*.jar
%{_javadir}/*.jar

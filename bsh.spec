Summary:        Lightweight Scripting for Java
Name:           bsh
Version:        1.3.0
Release:        26
License:        SPL or LGPLv2+
Group:          Development/Java
Url:            http://www.beanshell.org/
Source0:        %{name}-%{version}-src.tar.bz2
#cvs -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell login
#cvs -z3 -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell export -r rel_1_3_0_final BeanShell
#tar cjf bsh-1.3.0-src.tar.bz2 BeanShell
Source1:        bsh-1.3.0.pom
Source2:        bsh-bsf-1.3.0.pom
Source3:        %{name}-desktop.desktop
Patch0:         %{name}-build.patch
Patch1:         %{name}-xsl-fixes.patch
BuildArch:      noarch

BuildRequires:  java-1.6.0-openjdk-devel >= 0:1.6.0
BuildRequires:  ant bsf imagemagick desktop-file-utils
BuildRequires:  servlet
BuildRequires:  xalan-j2
BuildRequires:  xml-commons-apis
BuildRequires:	jpackage-utils
Requires:	jpackage-utils
Requires:       java >= 0:1.6.0
Requires:       bsf

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java. BeanShell executes
standard Java statements and expressions, in addition to obvious
scripting commands and syntax. BeanShell supports scripted objects as
simple method closures like those in Perl and JavaScript(tm).
You can use BeanShell interactively for Java experimentation and
debugging or as a simple scripting engine for your applications. In
short: BeanShell is a dynamically interpreted Java, plus some useful
stuff. Another way to describe it is to say that in many ways BeanShell
is to Java as Tcl/Tk is to C: BeanShell is embeddable - You can call
BeanShell from your Java applications to execute Java code dynamically
at run-time or to provide scripting extensibility for your applications.
Alternatively, you can call your Java applications and objects from
BeanShell; working with Java objects and APIs dynamically. Since
BeanShell is written in Java and runs in the same space as your
application, you can freely pass references to "real live" objects into
scripts and return them as results.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary:        Demo for %{name}
Group:          Development/Java
AutoReqProv:    no
Requires:       %{name} = %{version}-%{release}
Requires:       /usr/bin/env

%description demo
Demonstrations and samples for %{name}.

%package utils
Summary:        %{name} utilities
Group:          Development/Java
Requires:       %{name} = %{version}-%{release}
Requires:       jline
Provides:       %{name}-desktop = %{version}-%{release}
Obsoletes:      %{name}-desktop < 0:1.3.0-17
# So that yum will pull this in on base package upgrades from < 0:1.3.0-17
# (bsh and bshdoc scripts moved here in -17):
Obsoletes:      %{name} < 0:1.3.0-17

%description utils
%{name} utilities.

%prep
%setup -q -n BeanShell
%patch0 -p1
%patch1 -p1
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done
# remove all CVS files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
for file in `find . -type f -name .cvsignore`; do rm -rf $file; done
# fix rpmlint spurious-executable-perm warnings
for i in backbutton forwardbutton homebutton remoteconsole upbutton; do
    chmod 644 docs/images/$i.gif
done

%build
mkdir -p lib
pushd lib
ln -sf $(build-classpath bsf)
ln -sf $(build-classpath servlet)
ln -sf $(build-classpath xalan-j2-serializer)
popd
export CLASSPATH=$CLASSPATH:$(build-classpath xalan-j2-serializer)
ant="ant -Dant.build.javac.source=1.5"
$ant dist
%ifnarch ppc64 s390x
(cd docs/faq && $ant)
(cd docs/manual && $ant)
%endif

%install
# jars
install -d -m 755 %{buildroot}%{_javadir}
install -m 644 dist/%{name}-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-%{version}.jar
install -m 644 dist/%{name}-bsf-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-bsf-%{version}.jar
install -m 644 dist/%{name}-classpath-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-classpath-%{version}.jar
install -m 644 dist/%{name}-commands-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-commands-%{version}.jar
install -m 644 dist/%{name}-core-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-core-%{version}.jar
install -m 644 dist/%{name}-reflect-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-reflect-%{version}.jar
install -m 644 dist/%{name}-util-%{version}.jar \
             %{buildroot}%{_javadir}/%{name}-util-%{version}.jar

(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} ${jar/-%{version}/}; done)
%add_to_maven_depmap %{name} %{name} %{version} JPP %{name}
%add_to_maven_depmap %{name} %{name}-bsf %{version} JPP %{name}-bsf

# poms
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    %{buildroot}%{_datadir}/maven2/poms/JPP-%{name}.pom
install -pm 644 %{SOURCE2} \
    %{buildroot}%{_datadir}/maven2/poms/JPP-%{name}-bsf.pom

# manual
find docs -name ".cvswrappers" -exec rm -f {} \;
find docs -name "*.xml" -exec rm -f {} \;
find docs -name "*.xsl" -exec rm -f {} \;
find docs -name "*.log" -exec rm -f {} \;
%ifnarch ppc64 s390x
(cd docs/manual && mv html/* .)
(cd docs/manual && rm -rf html)
(cd docs/manual && rm -rf xsl)
%endif
# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}
# menu entry
desktop-file-install --vendor=fedora --mode=644 \
  --dir=%{buildroot}%{_datadir}/applications %{SOURCE3}
install -d -m 755 %{buildroot}%{_datadir}/icons/hicolor/16x16/apps
convert src/bsh/util/lib/icon.gif \
  %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/bsh.png

# demo
for i in `find tests -name \*.bsh`; do
  perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!/usr/bin/env %{_bindir}/%{name},' $i
  if head -1 $i | grep '#!/usr/bin/env %{_bindir}/%{name}' >/dev/null; then
    chmod 755 $i
  else
    chmod a+r $i
  fi
done
for i in `find tests -name \*.java -o -name \*.gif -o -name \*.txt`; do
  chmod 644 $i
done
chmod 755 tests/Template
cat > one << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/one >> one
cat one > tests/Interactive/reload/one
rm one
cat > two << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/two >> two
cat two > tests/Interactive/reload/two
rm two
install -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -pr tests %{buildroot}%{_datadir}/%{name}
install -d -m 755 %{buildroot}%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet.war %{buildroot}%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet-wbsh.war %{buildroot}%{_datadir}/%{name}/webapps

# scripts
install -d %{buildroot}%{_bindir}

function bsh_script() {
    local jars=%{name}.jar runclass=
    if [ $2 = jline.ConsoleRunner ] ; then
        jars="$jars jline.jar"
        runclass=bsh.Interpreter
    fi
cat > %{buildroot}%{_bindir}/$1 << EOF
#!/bin/sh
#
# $1 script
# JPackage Project (http://jpackage.sourceforge.net)

# Source functions library
_prefer_jre=true
. %{_datadir}/java-utils/java-functions

# Source system prefs
if [ -f %{_sysconfdir}/%{name}.conf ] ; then
  . %{_sysconfdir}/%{name}.conf
fi

# Source user prefs
if [ -f \$HOME/.%{name}rc ] ; then
  . \$HOME/.%{name}rc
fi

# Configuration
MAIN_CLASS=$2
if [ -n "\$BSH_DEBUG" ]; then
  BASE_FLAGS=-Ddebug=true
fi

BASE_JARS="$jars"

# Set parameters
set_jvm
set_classpath \$BASE_JARS
set_flags \$BASE_FLAGS
set_options \$BASE_OPTIONS

# Let's start
run $runclass "\$@"
EOF
}

bsh_script bsh jline.ConsoleRunner
bsh_script bsh-desktop bsh.Console

cat > %{buildroot}%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
cat scripts/bshdoc.bsh >> %{buildroot}%{_bindir}/%{name}doc

%post utils
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%post
%update_maven_depmap

%postun utils
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%postun
%update_maven_depmap

%posttrans utils
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc src/Changes.html src/License.txt src/README.txt
%{_javadir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/webapps
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}

%ifnarch ppc64 s390x
%files manual
%doc docs/*
%endif

%files javadoc
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%files demo
%doc tests/README.txt tests/Interactive/README
%{_datadir}/%{name}/tests/*

%files utils
%{_bindir}/%{name}*
%{_datadir}/applications/*%{name}-desktop.desktop
%{_iconsdir}/hicolor/*x*/apps/%{name}.png


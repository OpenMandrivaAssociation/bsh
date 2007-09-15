# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section        free

Name:           bsh
Version:        1.3.0
Release:        %mkrel 11.0.3
Epoch:          0
Summary:        Lightweight Scripting for Java
License:        LGPL
Source0:        %{name}-%{version}-src.tar.bz2
Source1:        bsh-1.3.0.pom
Source2:        bsh-bsf-1.3.0.pom

Patch0:         %{name}-build.patch
#Patch1:         %{name}-readline.patch
BuildRequires:  ant
BuildRequires:  bsf
BuildRequires:  perl
Requires:       bsf
Requires:       jpackage-utils >= 0:1.7.2
#BuildRequires:  libreadline-java
Url:            http://www.beanshell.org/
Group:          Development/Java
%if ! %{gcj_support}
Buildarch:      noarch
BuildRequires:  java-devel
%endif
Buildroot:      %{_tmppath}/%{name}-%{version}-buildroot

%if %{gcj_support}
BuildRequires:       java-gcj-compat-devel
%endif

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
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       /usr/bin/env

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n BeanShell
%patch0 -p1
#%patch1 -p1
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done
# remove all CVS files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
for file in `find . -type f -name .cvsignore`; do rm -rf $file; done

%build
mkdir -p lib
pushd lib
ln -sf $(build-classpath bsf)
ln -sf $(build-classpath servlet)
popd
%{ant} dist
(cd docs/faq && %{ant})
(cd docs/manual && %{ant})


%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{name}-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -m 644 dist/%{name}-bsf-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-bsf-%{version}.jar
install -m 644 dist/%{name}-classpath-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-classpath-%{version}.jar
install -m 644 dist/%{name}-commands-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-commands-%{version}.jar
install -m 644 dist/%{name}-core-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-core-%{version}.jar
install -m 644 dist/%{name}-reflect-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-reflect-%{version}.jar
install -m 644 dist/%{name}-util-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}-util-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} ${jar/-%{version}/}; done)

%add_to_maven_depmap %{name} %{name} %{version} JPP %{name}
%add_to_maven_depmap %{name} %{name}-bsf %{version} JPP %{name}-bsf

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsf.pom

# manual
find docs -name ".cvswrappers" -exec rm -f {} \;
find docs -name "*.xml" -exec rm -f {} \;
find docs -name "*.xsl" -exec rm -f {} \;
find docs -name "*.log" -exec rm -f {} \;
(cd docs/manual && mv html/* .)
(cd docs/manual && rm -rf html)
(cd docs/manual && rm -rf xsl)

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# demo
for i in `find tests -name \*.bsh`; do
  perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!/usr/bin/env %{_bindir}/%{name},' $i
  if head -1 $i | grep '#!/usr/bin/env %{_bindir}/%{name}' >/dev/null; then
    chmod 755 $i
  fi
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
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr tests $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet-wbsh.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps

# scripts
install -d $RPM_BUILD_ROOT%{_bindir}

cat > $RPM_BUILD_ROOT%{_bindir}/%{name} << EOF
#!/bin/sh
#
# %{name} script
# JPackage Project (http://jpackage.sourceforge.net)

# Source functions library
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
MAIN_CLASS=bsh.Interpreter
if [ -n "\$BSH_DEBUG" ]; then
  BASE_FLAGS=-Ddebug=true
fi

BASE_JARS="%{name}.jar"

#if [ -f /usr/lib/libJavaReadline.so ]; then
#  BASE_FLAGS="$BASE_FLAGS -Djava.library.path=/usr/lib"
#  BASE_FLAGS="\$BASE_FLAGS -Dbsh.console.readlinelib=GnuReadline"
#  BASE_JARS="\$BASE_JARS libreadline-java.jar"
#fi

# Set parameters
set_jvm
set_classpath \$BASE_JARS
set_flags \$BASE_FLAGS
set_options \$BASE_OPTIONS

# Let's start
run "\$@"
EOF

cat > $RPM_BUILD_ROOT%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
cat scripts/bshdoc.bsh >> $RPM_BUILD_ROOT%{_bindir}/%{name}doc

%if %{gcj_support}
export CLASSPATH=$(build-classpath gnu-crypto)
%{_bindir}/aot-compile-rpm \
   --exclude %{_datadir}/%{name}/webapps/bshservlet.war \
   --exclude %{_datadir}/%{name}/webapps/bshservlet-wbsh.war
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%doc src/Changes.html src/License.txt src/README.txt
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/%{name}doc
%{_javadir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/webapps
%{_datadir}/maven2/poms/*
%config(noreplace) %{_mavendepmapfragdir}/*
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files manual
%defattr(-,root,root)
%doc docs/*

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%files demo
%defattr(-,root,root)
%doc tests/README.txt tests/Interactive/README
%{_datadir}/%{name}/tests

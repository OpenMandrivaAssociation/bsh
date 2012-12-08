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

Name:           bsh
Version:        1.3.0
Release:        21
Summary:        Lightweight Scripting for Java
License:        SPL or LGPLv2+
Source0:        %{name}-%{version}-src.tar.bz2
#cvs -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell login
#cvs -z3 -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell export -r rel_1_3_0_final BeanShell
#tar cjf bsh-1.3.0-src.tar.bz2 BeanShell
Source1:        bsh-1.3.0.pom
Source2:        bsh-bsf-1.3.0.pom
Source3:        %{name}-desktop.desktop

Patch0:         %{name}-build.patch
Patch1:         %{name}-xsl-fixes.patch
BuildRequires:  java >= 0:1.6.0
BuildRequires:  ant, bsf, ant-trax, imagemagick, desktop-file-utils
BuildRequires:  servlet
BuildRequires:  xalan-j2
BuildRequires:  xml-commons-apis
Requires:       java >= 0:1.6.0
Requires:       bsf
Requires:       jpackage-utils >= 0:1.7.5-3.9
URL:            http://www.beanshell.org/
Group:          Development/Java
BuildArch:      noarch

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
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}-bsf.pom

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
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
# menu entry
desktop-file-install --vendor=fedora --mode=644 \
  --dir=$RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE3}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps
convert src/bsh/util/lib/icon.gif \
  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps/bsh.png

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
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr tests $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet-wbsh.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps

# scripts
install -d $RPM_BUILD_ROOT%{_bindir}

function bsh_script() {
    local jars=%{name}.jar runclass=
    if [ $2 = jline.ConsoleRunner ] ; then
        jars="$jars jline.jar"
        runclass=bsh.Interpreter
    fi
cat > $RPM_BUILD_ROOT%{_bindir}/$1 << EOF
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

cat > $RPM_BUILD_ROOT%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
cat scripts/bshdoc.bsh >> $RPM_BUILD_ROOT%{_bindir}/%{name}doc

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
%defattr(-,root,root)
%doc src/Changes.html src/License.txt src/README.txt
%{_javadir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/webapps
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}

%ifnarch ppc64 s390x
%files manual
%defattr(-,root,root)
%doc docs/*
%endif

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%files demo
%defattr(-,root,root)
%doc tests/README.txt tests/Interactive/README
%{_datadir}/%{name}/tests/*

%files utils
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/%{name}*
%{_datadir}/applications/*%{name}-desktop.desktop
%{_datadir}/icons/hicolor/*x*/apps/%{name}.png



%changelog
* Sun Nov 27 2011 Guilherme Moro <guilherme@mandriva.com> 1.3.0-20
+ Revision: 733861
- rebuild
- imported package bsh

  + Christophe Fergeau <cfergeau@mandriva.com>
    - rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild early 2009.0 package (before pixel changes)

* Fri May 23 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.3.0-11.0.4mdv2009.0
+ Revision: 210153
- remove gnu-crypto references and disable gcj_support

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.3.0-11.0.4mdv2008.1
+ Revision: 120806
- buildrequires java-rpmbuild

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.3.0-11.0.3mdv2008.0
+ Revision: 87263
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Wed Sep 05 2007 David Walluck <walluck@mandriva.org> 0:1.3.0-11.0.2mdv2008.0
+ Revision: 79666
- add javadoc link
- fix maven dir ownership
- fix gcj scriptlets
- remove file requires

* Tue Aug 28 2007 David Walluck <walluck@mandriva.org> 0:1.3.0-11.0.1mdv2008.0
+ Revision: 72560
- link to bsf
- fix Vendor and Distribution
- sync with jpackage
- Import bsh



* Mon Aug 07 2006 David Walluck <walluck@mandriva.org> 0:1.3.0-9.1.1mdv2007.0
- update and rebuild

* Mon Jun 05 2006 David Walluck <walluck@mandriva.org> 0:1.3.0-6.3mdv2007.0
- rebuild for libgcj.so.7
- own %%{_libdir}/gcj/%%{name}

* Fri Dec 02 2005 David Walluck <walluck@mandriva.org> 0:1.3.0-6.2mdk
- add post scripts

* Fri Dec 02 2005 David Walluck <walluck@mandriva.org> 0:1.3.0-6.1mdk
- aot-compile

* Sat Sep 10 2005 David Walluck <walluck@mandriva.org> 0:1.3.0-5.1mdk
- release

* Thu Jun 16 2005 Gary Benson <gbenson@redhat.com> 0:1.3.0-5jpp_1fc
- Build into Fedora.

* Thu Mar  4 2004 Frank Ch. Eigler <fche@redhat.com> 0:1.3.0-5jpp_1rh
- RH vacuuming
- added bsf build-prereq

* Mon Jan 26 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-5jpp
- really drop readline..patch

* Sun Jan 25 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-4jpp
- drop readline..patch

* Wed Jan 21 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-3jpp
- port libreadline-java patch to new bsh

* Tue Jan 20 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-2jpp
- add Distribution tag

* Tue Jan 20 2004 David Walluck <david@anti-microsoft.org> 0:1.3.0-1jpp
- 1.3.0
- remove bsf patch (fixed upstream)
- add epoch to demo package Requires

* Fri Apr 12 2003 David Walluck <david@anti-microsoft.org> 0:1.2-0.b8.4jpp
- fix strange permissions

* Fri Apr 11 2003 David Walluck <david@anti-microsoft.org> 0:1.2-0.b8.3jpp
- rebuild for JPackage 1.5
- add bsf..patch

* Sat Feb 01 2003 David Walluck <david@anti-microsoft.org> 1.2-0.b8.2jpp
- remove servlet dependency (if anyone wants to add this as a separate
  package and do the tomcat integration, be my guest)

* Thu Jan 23 2003 David Walluck <david@anti-microsoft.org> 1.2-0.b8.1jpp
- rename to bsh
- add manual
- add Changes.html to %%doc
- add bsh and bshdoc scripts
- add %%dir %%{_datadir}/%%{name} to main package
- correct test interpreter and make bsh files executable

* Mon Jan 21 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-3jpp
- really section macro

* Sun Jan 20 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-2jpp
- additional sources in individual archives
- versioned dir for javadoc
- no dependencies for javadoc package
- stricter dependency for demo package
- section macro

* Tue Dec 18 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.01-1jpp
- first JPackage release

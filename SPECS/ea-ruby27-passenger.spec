# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel
%global pkg ruby27
%global gem_name passenger
%global bundled_boost_version 1.60.0

# Force Software Collections on
%global _scl_prefix %{ns_dir}
%global scl %{ns_name}-%{pkg}
# HACK: OBS Doesn't support macros in BuildRequires statements, so we have
#       to hard-code it here.
# https://en.opensuse.org/openSUSE:Specfile_guidelines#BuildRequires
%global scl_prefix %{scl}-
%{?scl:%scl_package rubygem-%{gem_name}}

%global passenger_libdir    %{_datadir}/passenger
%global passenger_archdir   %{_libdir}/passenger
%global passenger_agentsdir %{_libexecdir}/passenger
%define ruby_vendorlibdir   %(scl enable ea-ruby27 "ruby -rrbconfig -e 'puts RbConfig::CONFIG[%q|vendorlibdir|]'")

# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define release_prefix 4

%global _httpd_mmn         %(cat %{_root_includedir}/apache2/.mmn 2>/dev/null || echo missing-ea-apache24-devel)
%global _httpd_confdir     %{_root_sysconfdir}/apache2/conf.d
%global _httpd_modconfdir  %{_root_sysconfdir}/apache2/conf.modules.d
%global _httpd_moddir      %{_root_libdir}/apache2/modules

%define ea_openssl_ver 1.1.1d-1
%define ea_libcurl_ver 7.68.0-2

Summary: Phusion Passenger application server
Name: %{?scl:%scl_prefix}rubygem-passenger
Version: 6.0.6
Release: %{release_prefix}%{?dist}.cpanel
Group: System Environment/Daemons
# Passenger code uses MIT license.
# Bundled(Boost) uses Boost Software License
# BCrypt and Blowfish files use BSD license.
# Documentation is CC-BY-SA
# See: https://bugzilla.redhat.com/show_bug.cgi?id=470696#c146
License: Boost and BSD and BSD with advertising and MIT and zlib
URL: https://www.phusionpassenger.com

# http://s3.amazonaws.com/phusion-passenger/releases/passenger-%%{version}.tar.gz
Source: passenger-%{version}.tar.gz
Source1: passenger.logrotate
Source2: rubygem-passenger.tmpfiles
Source3: cxxcodebuilder.tar.gz
Source10: apache-passenger.conf.in
Source12: config.json
# These scripts are needed only before we update httpd24-httpd.service
# in rhel7 to allow enabling extra SCLs.
Source13: ea-ruby27
Source14: passenger_apps.default
Source15: update_ruby_shebang.pl

# Use upstream libuv instead of the bundled libuv
Patch0:         0001-Patch-build-files-to-use-SCL-libuv-paths.patch
# httpd on RHEL7 is using private /tmp. This break passenger status.
# We workaround that by using "/var/run/ea-ruby27-passenger" instead of "/tmp".
Patch1:         0002-Avoid-using-tmp-for-the-TMPDIR.patch
# Load passenger_native_support.so from lib_dir
Patch2:         0003-Fix-the-path-for-passenger_native_support.patch
# Supress logging of empty messages
Patch3:         0004-Suppress-logging-of-empty-messages.patch
# Update the instance registry paths to include the SCL path
Patch4:         0005-Add-the-instance-registry-path-for-the-ea-ruby27-SCL.patch
# Build against ea-libcurl
Patch5:         0006-Use-ea-libcurl-instead-of-system-curl.patch
# Add a new directive to Passenger that will allow us to disallow
## Passenger directives in .htaccess files
Patch6:         0007-Add-new-PassengerDisableHtaccess-directive.patch

BuildRequires: tree

BuildRequires: ea-apache24-devel
BuildRequires: %{?scl:%scl_prefix}ruby
BuildRequires: %{?scl:%scl_prefix}ruby-devel
BuildRequires: %{?scl:%scl_prefix}rubygems
BuildRequires: %{?scl:%scl_prefix}rubygems-devel
BuildRequires: %{?scl:%scl_prefix}rubygem(rake) >= 0.8.1
BuildRequires: %{?scl:%scl_prefix}rubygem(rack)
Requires: %{?scl:%scl_prefix}rubygem(rack)
# Required for testing, but tests are disabled cause they failed.
BuildRequires: %{?scl:%scl_prefix}rubygem(sqlite3)
BuildRequires: %{?scl:%scl_prefix}rubygem(mizuho)

BuildRequires: perl

%if 0%{?rhel} < 8
BuildRequires: ea-libcurl >= %{ea_libcurl_ver}
BuildRequires: ea-libcurl-devel >= %{ea_libcurl_ver}
BuildRequires: ea-brotli ea-brotli-devel
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11-devel >= %{ea_openssl_ver}
%else
BuildRequires: curl
BuildRequires: libcurl
BuildRequires: libcurl-devel
BuildRequires: brotli
BuildRequires: brotli-devel
BuildRequires: openssl-devel
BuildRequires: libnghttp2
BuildRequires: python2
Requires: python2
%endif

%if 0%{?rhel} >= 8
# NOTE: our macros.scl insists that I use python3.  Too much risk on the
# scripts
%global __os_install_post %{expand:
    /usr/lib/rpm/brp-scl-compress %{_scl_root}
    %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}
    /usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump}
    }
    /usr/lib/rpm/brp-strip-static-archive %{__strip}
    /usr/lib/rpm/brp-scl-python-bytecompile /usr/bin/python2 %{?_python_bytecompile_errors_terminate_build} %{_scl_root}
    /usr/lib/rpm/brp-python-hardlink
%{nil}}
%endif

BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: %{?scl:%scl_prefix}libuv-devel

BuildRequires: scl-utils
BuildRequires: scl-utils-build
%{?scl:BuildRequires: %{scl}-runtime}
%{?scl:Requires:%scl_runtime}

%if 0%{?rhel} < 8
Requires: ea-libcurl >= %{ea_libcurl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%else
Requires: libcurl
Requires: openssl
%endif

Provides: bundled(boost) = %{bundled_boost_version}

# Suppress auto-provides for module DSO
%{?filter_provides_in: %filter_provides_in %{_httpd_moddir}/.*\.so$}
%{?filter_setup}

%description
Phusion Passenger(r) is a web server and application server, designed to be fast,
robust and lightweight. It takes a lot of complexity out of deploying web apps,
adds powerful enterprise-grade features that are useful in production,
and makes administration much easier and less complex. It supports Ruby,
Python, Node.js and Meteor.

%package -n %{scl_prefix}mod_passenger
Summary: Apache Module for Phusion Passenger
Group: System Environment/Daemons
BuildRequires:  ea-apache24-devel
Requires: ea-apache24-mmn = %{_httpd_mmn}
Requires: %{scl_prefix}ruby-wrapper
Requires: %{name}%{?_isa} = %{version}-%{release}
License: Boost and BSD and BSD with advertising and MIT and zlib
Provides: apache24-passenger
Conflicts: apache24-passenger

%description -n %{scl_prefix}mod_passenger
This package contains the pluggable Apache server module for Phusion Passenger(r).

%package doc
Summary: Phusion Passenger documentation
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
License: CC-BY-SA and MIT and (MIT or GPL+)

%description doc
This package contains documentation files for Phusion Passenger(r).

%package -n %{?scl:%scl_prefix}ruby-wrapper
Summary:   Phusion Passenger application server for %{scl_prefix}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: %{?scl:%scl_prefix}ruby

%description -n %{?scl:%scl_prefix}ruby-wrapper
Phusion Passenger application server for %{scl_prefix}.

%prep
%setup -q %{?scl:-n %{gem_name}-release-%{version}}

%patch0 -p1 -b .libuv
%patch1 -p1 -b .tmpdir
%patch2 -p1 -b .nativelibdir
%patch3 -p1 -b .emptymsglog
%patch4 -p1 -b .instanceregpath
%if 0%{?rhel} < 8
%patch5 -p1 -b .useeacurl
%endif
%patch6 -p1 -b .disablehtaccess
echo SOURCE15 %{SOURCE15}
cp %{SOURCE15} .

tar -xf %{SOURCE3}

# Don't use bundled libuv
rm -rf src/cxx_supportlib/vendor-modified/libuv

# Find files with a hash-bang that do not have executable permissions
for script in `find . -type f ! -perm /a+x -name "*.rb"`; do
    [ ! -z "`head -n 1 $script | grep \"^#!/\"`" ] && chmod -v 755 $script
    /bin/true
done

%build
# Build the complete Passenger and shared module against ruby27.

%{?scl:scl enable ea-ruby27 - << \EOF}
echo "BUILD: 001"
export LD_LIBRARY_PATH=%{_libdir}:$LD_LIBRARY_PATH
echo "BUILD: 002"
export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=false
export GEM_PATH=%{gem_dir}:${GEM_PATH:+${GEM_PATH}}${GEM_PATH:-`scl enable ea-ruby27 -- ruby -e "print Gem.path.join(':')"`}
echo "BUILD: 003"
CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;
echo "BUILD: 004"
%if 0%{?rhel} < 8
EXTRA_CXX_LDFLAGS="-L/opt/cpanel/ea-ruby27/root/usr/lib64 -L/opt/cpanel/ea-openssl11/%{_lib} -L/opt/cpanel/ea-brotli/%{_lib} -Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-brotli/%{_lib} -Wl,-rpath=/opt/cpanel/libcurl/%{_lib}  -Wl,-rpath=%{_libdir},--enable-new-dtags "; export EXTRA_CXX_LDFLAGS;
%else
echo "LIBDIR" %{_libdir}
EXTRA_CXX_LDFLAGS="-L/opt/cpanel/ea-ruby27/root/usr/lib64 -L/usr/lib64 -lcurl -lssl -lcrypto -lgssapi_krb5 -lkrb5 -lk5crypto -lkrb5support -lssl -lcrypto -lssl -lcrypto -Wl,-rpath=%{_libdir},--enable-new-dtags -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto "; export EXTRA_CXX_LDFLAGS;
echo $EXTRA_CXX_LDFLAGS
%endif
echo "BUILD: 005"

FFLAGS="${FFLAGS:-%optflags}" ; export FFLAGS;
echo "BUILD: 006"
echo "EXTRA_CXX_LDFLAGS" $EXTRA_CXX_LDFLAGS

%if 0%{?rhel} < 8
export EXTRA_CXXFLAGS="-I/opt/cpanel/ea-openssl11/include -I/opt/cpanel/libcurl/include -I/opt/cpanel/ea-ruby27/root/usr/include"
%else
export EXTRA_CXXFLAGS="-I/opt/cpanel/ea-ruby27/root/usr/include -I/usr/include"
%endif

echo "BUILD: 007"
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
echo "BUILD: 008"

rake fakeroot \
    NATIVE_PACKAGING_METHOD=rpm \
    FS_PREFIX=%{_prefix} \
    FS_BINDIR=%{_bindir} \
    FS_SBINDIR=%{_sbindir} \
    FS_DATADIR=%{_datadir} \
    FS_LIBDIR=%{_libdir} \
    FS_DOCDIR=%{_docdir} \
    RUBYLIBDIR=%{passenger_libdir} \
    RUBYARCHDIR=%{passenger_archdir} \
    APACHE2_MODULE_PATH=%{_httpd_moddir}/mod_passenger.so

%{?scl:EOF}
echo "BUILD: 009"

# find python and ruby scripts to change their shebang

echo "Python"
find . -name "*.py" -print | xargs sed -i '1s:^#!.*python.*$:#!/usr/bin/python2:'

echo "Ruby"
find . -name "*.rb" -print | xargs sed -i '1s:^#!.*ruby.*$:#!/opt/cpanel/ea-ruby27/root/usr/bin/ruby:'

echo "BUILD: 010"
find . -type f -print
echo "BUILD: END"

%install

echo "INSTALL: 001"

echo "TREE"
find . -type f -print

echo "INSTALL: 002"

mkdir -p %{buildroot}/opt/cpanel/ea-ruby27/src/passenger-release-%{version}/
tar xzf %{SOURCE0} -C %{buildroot}/opt/cpanel/ea-ruby27/src/
tar xzf %{SOURCE3} -C %{buildroot}/opt/cpanel/ea-ruby27/src/passenger-release-%{version}/

echo "INSTALL: 003"

%{?scl:scl enable ea-ruby27 - << \EOF}
export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=false

export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8

cp -a pkg/fakeroot/* %{buildroot}/

# Install bootstrapping code into the executables and the Nginx config script.
./dev/install_scripts_bootstrap_code.rb --ruby %{passenger_libdir} %{buildroot}%{_bindir}/* %{buildroot}%{_sbindir}/*
%{?scl:EOF}

# Install Apache module.
mkdir -p %{buildroot}/%{_httpd_moddir}
install -pm 0755 buildout/apache2/mod_passenger.so %{buildroot}/%{_httpd_moddir}

# Install Apache config.
mkdir -p %{buildroot}%{_httpd_confdir} %{buildroot}%{_httpd_modconfdir}
sed -e 's|@PASSENGERROOT@|%{passenger_libdir}/phusion_passenger/locations.ini|g' %{SOURCE10} > passenger.conf
sed -i 's|@PASSENGERDEFAULTRUBY@|%{_libexecdir}/passenger-ruby27|g' passenger.conf
sed -i 's|@PASSENGERSO@|%{_httpd_moddir}/mod_passenger.so|g' passenger.conf
sed -i 's|@PASSENGERINSTANCEDIR@|%{_localstatedir}/run/passenger-instreg|g' passenger.conf

mkdir -p %{buildroot}/var/cpanel/templates/apache2_4
install -m 0640 %{SOURCE14} %{buildroot}/var/cpanel/templates/apache2_4/passenger_apps.default

%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
    sed -n /^LoadModule/p passenger.conf > 10-passenger.conf
    sed -i /^LoadModule/d passenger.conf
    touch -r %{SOURCE10} 10-passenger.conf
    install -pm 0644 10-passenger.conf %{buildroot}%{_httpd_modconfdir}/passenger.conf
%endif
touch -r %{SOURCE10} passenger.conf
install -pm 0644 passenger.conf %{buildroot}%{_httpd_confdir}/passenger.conf

# Install wrapper script to allow using the SCL Ruby binary via apache
%{__mkdir_p} %{buildroot}%{_libexecdir}/
install -pm 0755 %{SOURCE13} %{buildroot}%{_libexecdir}/passenger-ruby27

# Move agents to libexec
mkdir -p %{buildroot}/%{passenger_agentsdir}
mv %{buildroot}/%{passenger_archdir}/support-binaries/* %{buildroot}/%{passenger_agentsdir}
rmdir %{buildroot}/%{passenger_archdir}/support-binaries/
sed -i 's|%{passenger_archdir}/support-binaries|%{passenger_agentsdir}|g' \
    %{buildroot}%{passenger_libdir}/phusion_passenger/locations.ini

# Instance registry to track apps
mkdir -p %{buildroot}%{_localstatedir}/run/passenger-instreg

# tmpfiles.d
%if 0%{?rhel} > 6
    mkdir -p %{buildroot}/var/run
    mkdir -p %{buildroot}%{_root_prefix}/lib/tmpfiles.d
    install -m 0644 %{SOURCE2} %{buildroot}%{_root_prefix}/lib/tmpfiles.d/%{scl_prefix}passenger.conf
    install -d -m 0755 %{buildroot}/var/run/%{scl_prefix}passenger
%else
    mkdir -p %{buildroot}/var/run/%{scl_prefix}passenger
%endif

# Install man pages into the proper location.
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_mandir}/man8
cp man/*.1 %{buildroot}%{_mandir}/man1
cp man/*.8 %{buildroot}%{_mandir}/man8

# Fix Python scripts with shebang which are not executable
chmod +x %{buildroot}%{_datadir}/passenger/helper-scripts/wsgi-loader.py

# Remove empty release.txt file
rm -f %{buildroot}%{_datadir}/passenger/release.txt

# Remove object files and source files. They are needed to compile nginx
# using "passenger-install-nginx-module", but it's not according to
# guidelines. Debian does not provide these files too, so we stay consistent.
# In the long term, it would be better to allow Fedora nginx to support
# Passenger.
rm -rf %{buildroot}%{passenger_libdir}/ngx_http_passenger_module
rm -rf %{buildroot}%{passenger_libdir}/ruby_extension_source
rm -rf %{buildroot}%{passenger_libdir}/include
rm -rf %{buildroot}%{passenger_archdir}/nginx_dynamic
rm -rf %{buildroot}%{_libdir}/passenger/common
rm -rf %{buildroot}%{_bindir}/passenger-install-*-module

mkdir -p %{buildroot}%{ruby_vendorlibdir}/passenger
cp %{buildroot}/%{passenger_archdir}/*.so %{buildroot}%{ruby_vendorlibdir}/passenger/

echo "INSTALL: 098"
echo ruby_vendorlibdir %{ruby_vendorlibdir}
find %{buildroot}/opt/cpanel/ea-ruby27/root/usr  -type f -print

echo "INSTALL: 099"
echo "Ruby"

cd %{buildroot}/opt/cpanel/ea-ruby27/src
echo %{SOURCE15}
perl %{SOURCE15}
cd -

%check
%{?scl:scl enable ea-ruby27 - << \EOF}
export USE_VENDORED_LIBEV=true
export USE_VENDORED_LIBUV=false

# Running the full test suite is not only slow, but also impossible
# because not all requirements are packaged by Fedora. It's also not
# too useful because Phusion Passenger is automatically tested by a CI
# server on every commit. The C++ tests are the most likely to catch
# any platform-specific bugs (e.g. bugs caused by wrong compiler options)
# so we only run those. Note that the C++ tests are highly timing
# sensitive, so sometimes they may fail even though nothing is really
# wrong. We therefore do not make failures fatal, although the result
# should still be checked.
# Currently the tests fail quite often on ARM because of the slower machines.
# Test are not included in the tarballs now :'(
# cp %{SOURCE12} test/config.json
# rake test:cxx || true
%{?scl:EOF}

%files
%doc LICENSE CONTRIBUTORS CHANGELOG
%{_bindir}/passenger*
%if 0%{?rhel} > 6
%{_root_prefix}/lib/tmpfiles.d/*.conf
%endif
%dir /var/run/%{scl_prefix}passenger
%dir %attr(755, root, root) %{_localstatedir}/run/passenger-instreg
%{passenger_libdir}
%{passenger_archdir}
%{passenger_agentsdir}
%{ruby_vendorlibdir}/passenger/
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*

%files -n %{?scl:%scl_prefix}ruby-wrapper
%doc LICENSE CONTRIBUTORS CHANGELOG
%{_libexecdir}/passenger-ruby27

%files doc
%doc %{_docdir}/passenger

%files -n %{scl_prefix}mod_passenger
%config(noreplace) %{_httpd_modconfdir}/*.conf
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_confdir}/*.conf
%endif
/var/cpanel/templates/apache2_4/passenger_apps.default
%{_httpd_moddir}/mod_passenger.so
/opt/cpanel/ea-ruby27/src/passenger-release-%{version}/

%changelog
* Mon Dec 07 2020 Travis Holloway <t.holloway@cpanel.net> - 6.0.6-4
- ZC-8082: Do not apply ea-libcurl patch on C8 builds

* Mon Dec 07 2020 Daniel Muey <dan@cpanel.net> - 6.0.6-3
- ZC-7655: Provide/Conflict `apache24-passenger`

* Tue Dec 01 2020 Julian Brown <julian.brown@cpanel.net> - 6.0.6-2
- ZC-7974: Require rack

* Tue Sep 08 2020 Julian Brown <julian.brown@cpanel.net> - 6.0.6-1
- ZC-7508: Initial Commit


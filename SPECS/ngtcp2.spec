# Supported targets: el8, el9, el10

# el10 adds /usr/lib/rpm/check-rpaths which won't pass because we use
# non-standard rpaths for aws-lc libraries, which is on purpose
%global __brp_check_rpaths %{nil}

%define _prefix /opt/%{name}
%define _docdir_fmt ngtcp2

%{!?make_verbose: %define make_verbose 0}

%if 0%{?rhel} <= 8
%undefine __cmake_in_source_build
%endif

%global source_date_epoch_from_changelog 0

Name: ngtcp2-0z
Version: 1.19.0
Release: 1%{?dist}.zenetys
Summary: ngtcp2 library implementing RFC9000 QUIC protocol
License: MIT
URL: https://github.com/ngtcp2/ngtcp2

Source0: https://github.com/ngtcp2/ngtcp2/archive/refs/tags/v%{version}.tar.gz#/ngtcp2-%{version}.tar.gz

Patch100: ngtcp2-boringssl-shared-cmake.patch
Patch101: ngtcp2-cmake-lib-only.patch

BuildRequires: aws-lc-0z-devel
BuildRequires: cmake >= 3.20
BuildRequires: gcc-c++

%description
The ngtcp2 project is an effort to implement RFC9000 QUIC protocol.

%prep
%setup -n ngtcp2-%{version}
%patch100 -p1
%patch101 -p1

%build
%cmake \
    %if !%{make_verbose}
    -DCMAKE_VERBOSE_MAKEFILE=OFF \
    %endif
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DENABLE_LIB_ONLY=ON \
    -DENABLE_STATIC_LIB=OFF \
    -DENABLE_OPENSSL=OFF \
    -DENABLE_BORINGSSL=ON \
    -DBORINGSSL_INCLUDE_DIR='%{aws_lc_0z_prefix}/include' \
    -DBORINGSSL_LIBRARIES='-L%{aws_lc_0z_prefix}/%{_lib} -lssl -lcrypto' \
    -DBORINGSSL_INSTALL_RPATH='$ORIGIN:%{aws_lc_0z_prefix}/%{_lib}'

# use --define 'make_verbose 1' to enable verbose
%(x='%{cmake_build}'; echo ${x/ --verbose})

%install
%cmake_install
rm -rf %{buildroot}%{_prefix}/lib/cmake

mkdir -p %{buildroot}%{_rpmmacrodir}
echo '%%%(echo %{name} |tr '-' '_')_prefix %{_prefix}' \
    > %{buildroot}%{_rpmmacrodir}/macros.%{name}

%files
%doc README.rst
%license COPYING

%{_libdir}/libngtcp2.so.*
%{_libdir}/libngtcp2_crypto_boringssl.so

%package devel
Summary: ngtcp2 development files from package %{name}
Requires: %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description devel
ngtcp2 development files from package %{name}.

%files devel
%{_includedir}/ngtcp2
%{_libdir}/libngtcp2.so
%{_libdir}/pkgconfig/libngtcp2.pc
%{_libdir}/pkgconfig/libngtcp2_crypto_boringssl.pc
%{_rpmmacrodir}/macros.%{name}

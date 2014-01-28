%define _unpackaged_files_terminate_build 0
%define name blackbird-nginx
%define version 0.1.4
%define unmangled_version 0.1.4
%define release 2

%define blackbird_conf_dir /etc/blackbird/conf.d

Summary: Get monitorring stats of nginx for blackbird
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: makocchi <makocchi@gmail.com>
Packager: makocchi <makocchi@gmail.com>
Requires:  blackbird
Requires:  python-requests
Url: https://github.com/Vagrants/blackbird-nginx
BuildRequires:  python-devel

%description
Project Info
============

* Project Page: https://github.com/Vagrants/blackbird-nginx


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --skip-build --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/%{blackbird_conf_dir}
cp -p nginx.cfg $RPM_BUILD_ROOT/%{blackbird_conf_dir}/nginx.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Tue Jan 28 2014 makochi <makocchi@gmail.com> - 0.1.4-2
- fix subprocess problem
- add plugin version to send item

* Tue Jan 28 2014 makochi <makocchi@gmail.com> - 0.1.4-1
- update to 0.1.4

* Thu Jan  9 2014 makochi <makocchi@gmail.com> - 0.1.3-1
- update to 0.1.3

* Mon Jan  6 2014 makochi <makocchi@gmail.com> - 0.1.2-1
- update to 0.1.2

* Wed Nov 25 2013 makochi <makocchi@gmail.com> - 0.1.1-1
- update to 0.1.1

* Tue Nov 24 2013 makochi <makocchi@gmail.com> - 0.1.0-1
- first package

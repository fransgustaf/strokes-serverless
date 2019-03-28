FROM amazonlinux

RUN yum -y install python3-pip shadow-utils emacs-nox passwd sudo mlocate MySQL-python python3-devel mysql-devel gcc gcc-c++ virtualenv

RUN updatedb

RUN adduser gustaf
RUN usermod -G wheel gustaf

RUN chown root:wheel /usr/local/lib/
RUN chown root:wheel /usr/local/bin/
RUN chown root:wheel /usr/local/lib64/
RUN chmod 775 /usr/local/lib/
RUN chmod 775 /usr/local/bin/
RUN chmod 775 /usr/local/lib64/

# pip3 install awscli sqlalchemy python-lambda-local mysql-connector mysqlclient requests
# pip install mysql-connector
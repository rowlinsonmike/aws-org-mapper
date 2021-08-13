
<p align="center">
  <img height="100px" src="https://image.flaticon.com/icons/png/512/1188/1188908.png" alt="flaticon"/>
</p>

    
# aws-org-mapper

Generates diagrams of each AWS Organization account showing its associated organizational units, service control policies, and applied permission sets from AWS SSO.


## Features

- scps applied to an account
- ou structure account is a part of
- permission sets applied to account from AWS SSO

  
## Requirements

- Python 3.7+
- boto3
- AWS credentials available to boto3
- 
## Usage/Examples

```python
python aws-org-mapper.py
```

creates a html file called `aws-org-mapper.html` inside of the directory where the script is executed.

## Acknowledgements

 - [Mermaid JS](https://mermaid-js.github.io/mermaid/#/) - used to construct diagram

## Authors

- [@rowlinsonmike](https://www.github.com/rowlinsonmike)

## License

[MIT](https://choosealicense.com/licenses/mit/)

  
from fastapi import APIRouter, BackgroundTasks
from services.smtpService import send_email
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter()

class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    order_id: str

@router.post("/send-email/")
async def send_email_endpoint(email: EmailSchema, background_tasks: BackgroundTasks):

    body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invoice</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                
                .invoice-box {
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 30px;
                    border: 1px solid #eee;
                    background-color: #fff;
                }
                
                table {
                    width: 100%;
                    line-height: inherit;
                    text-align: left;
                    border-collapse: collapse;
                }
                
                table td {
                    padding: 8px;
                    vertical-align: top;
                }
                
                table tr.top table td {
                    padding-bottom: 20px;
                }
                
                table tr.top table td.title {
                    font-size: 45px;
                    line-height: 45px;
                    color: #333;
                }
                
                table tr.information table td {
                    padding-bottom: 40px;
                }
                
                table tr.heading td {
                    background: #eee;
                    border-bottom: 1px solid #ddd;
                    font-weight: bold;
                    text-align: right;
                }
                
                table tr.item td {
                    border-bottom: 1px solid #eee;
                    text-align: right;
                }
                
                table tr.item.last td {
                    border-bottom: none;
                }
                
                table tr.total td:nth-child(2) {
                    border-top: 2px solid #eee;
                    font-weight: bold;
                    padding-top: 10px;
                    padding-bottom: 10px;
                }
                
                .terms {
                    margin-top: 40px;
                    font-size: 14px;
                }
                
                h2, p {
                    margin: 0;
                }
                
                h2 {
                    font-size: 22px;
                }
                
                .title p {
                    font-size: 14px;
                    line-height: 1.5;
                }
                
                .top td, .information td, .heading td, .item td, .total td {
                    font-size: 14px;
                }

                .left {
                    float: left;
                    width: 60%;
                }

                .right {
                    float: right;
                    width: 40%;
                    text-align: right;
                }

                .clearfix {
                    overflow: auto;
                }
            </style>
        </head>
        <body>
            <div class="invoice-box">
                <table>
                    <tr class="top">
                        <td colspan="5">
                            <div class="clearfix">
                                <div class="left">
                                    <h2>Zylker Electronics Hub</h2>
                                    <p>14B, Northern Street Greater South Avenue<br>
                                    New York New York 10001 U.S.A</p>
                                </div>
                                <div class="right">
                                    <p>INVOICE</p>
                                    <p>Invoice# : INV-000003<br>
                                    Invoice Date : 18 May 2023<br>
                                    Terms : Due on Receipt<br>
                                    Due Date : 18 May 2023</p>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr class="information">
                        <td colspan="5">
                            <div class="clearfix">
                                <div class="left">
                                    <p>Bill To</p>
                                    <p>Ms. Mary D. Dunton<br>
                                    1324 Hinkle Lake Road<br>
                                    Needham<br>
                                    02192 Maine</p>
                                </div>
                                <div class="right">
                                    <p>Ship To</p>
                                    <p>1324 Hinkle Lake Road<br>
                                    Needham<br>
                                    02192 Maine</p>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr class="heading">
                        <td>#</td>
                        <td>Item & Description</td>
                        <td>Qty</td>
                        <td>Rate</td>
                        <td>Amount</td>
                    </tr>
                    <tr class="item">
                        <td>1</td>
                        <td>Camera<br>DSLR camera with advanced shooting capabilities</td>
                        <td>1</td>
                        <td>$899.00</td>
                        <td>$899.00</td>
                    </tr>
                    <tr class="item">
                        <td>2</td>
                        <td>Fitness Tracker<br>Activity tracker with heart rate monitoring</td>
                        <td>1</td>
                        <td>$129.00</td>
                        <td>$129.00</td>
                    </tr>
                    <tr class="item">
                        <td>3</td>
                        <td>Laptop<br>Lightweight laptop with a powerful processor</td>
                        <td>1</td>
                        <td>$1,199.00</td>
                        <td>$1,199.00</td>
                    </tr>
                    <tr class="total">
                        <td colspan="4" style="text-align: right;">Sub Total</td>
                        <td style="text-align: right;">$2,227.00</td>
                    </tr>
                    <tr class="total">
                        <td colspan="4" style="text-align: right;">Tax Rate</td>
                        <td style="text-align: right;">5.00%</td>
                    </tr>
                    <tr class="total">
                        <td colspan="4" style="text-align: right;">Total</td>
                        <td style="text-align: right;">$2,338.35</td>
                    </tr>
                    <tr class="total">
                        <td colspan="4" style="text-align: right;">Balance Due</td>
                        <td style="text-align: right;">$2,338.35</td>
                    </tr>
                </table>
                <p class="terms">Thanks for shopping with us.</p>
                <p class="terms">Terms & Conditions<br>
                Full payment is due upon receipt of this invoice.<br>
                Late payments may incur additional charges or interest as per the applicable laws.</p>
            </div>
        </body>
        </html>
        """



    background_tasks.add_task(send_email, email.email, email.subject, email.order_id, body)
    return {"message": "Email has been sent"}
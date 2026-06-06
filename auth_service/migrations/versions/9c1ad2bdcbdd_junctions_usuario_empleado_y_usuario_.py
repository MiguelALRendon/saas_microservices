"""junctions usuario_empleado y usuario_sucursal, eliminar usuario.fkEmpleado

Revision ID: 9c1ad2bdcbdd
Revises: c926a6e86196
Create Date: 2026-06-06 11:22:48.213546

Notas:
 - Las tablas usuario_empleado y usuario_sucursal ya existen (creadas vía db.create_all);
   esta migración registra el cambio de modelo y migra los datos antiguos de usuario.fkEmpleado
   hacia la junction antes de eliminar la columna.
 - usuario.fkSistema se conserva intacto.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9c1ad2bdcbdd'
down_revision = 'c926a6e86196'
branch_labels = None
depends_on = None


def upgrade():
    # Backfill: copiar usuario.fkEmpleado a la junction usuario_empleado antes de eliminar la columna.
    op.execute(
        """
        INSERT INTO usuario_empleado (oid, fkUsuario, fkEmpleado, createdAt, updatedAt, estatus)
        SELECT UUID(), u.oid, u.fkEmpleado, NOW(), NOW(), 'ACTIVO'
        FROM usuario u
        WHERE u.fkEmpleado IS NOT NULL
          AND u.estatus != 'ELIMINADO'
          AND NOT EXISTS (
              SELECT 1 FROM usuario_empleado ue
              WHERE ue.fkUsuario = u.oid AND ue.fkEmpleado = u.fkEmpleado
          );
        """
    )

    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_usuario_fkEmpleado'))
        batch_op.drop_column('fkEmpleado')


def downgrade():
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fkEmpleado', mysql.VARCHAR(length=36), nullable=False))
        batch_op.create_index(batch_op.f('ix_usuario_fkEmpleado'), ['fkEmpleado'], unique=False)
